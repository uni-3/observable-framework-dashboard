#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb==1.4.3",
#     "python-dotenv",
#     "networkx",
# ]
# ///

import duckdb
import os
from dotenv import load_dotenv
from networkx.algorithms.community import greedy_modularity_communities
import sys
import json
import networkx as nx
from typing import TypedDict


class TypeNodeStats(TypedDict):
    """タイプノードの統計情報"""
    type_name: str
    total_count: int
    single_type_count: int
    single_type_rate: float
    degree_centrality: float
    eigenvector_centrality: float
    group: int
    community: int


class CoLink(TypedDict):
    """共起リンク"""
    source: str
    target: str
    value: int


class PokemonNode(TypedDict):
    """ポケモンノード"""
    name: str
    types: list[str]
    total_count: int
    group: int


class BipartiteLink(TypedDict):
    """二部グラフリンク"""
    source: str
    target: str


class NetworkOutput(TypedDict):
    """ネットワークデータの出力型定義"""
    type_nodes: list[TypeNodeStats]
    pokemon_nodes: list[PokemonNode]
    co_links: list[CoLink]
    bipartite_links: list[BipartiteLink]


def main() -> None:
    try:
        load_dotenv(".env.local")
        load_dotenv(".env")


        database: str | None = os.getenv("DUCKDB_DATABASE")
        if not database:
            raise ValueError("DUCKDB_DATABASE environment variable is not set.")

        con: duckdb.DuckDBPyConnection = duckdb.connect(database, read_only=True)

        # 単タイプ率の計算と属性の取得
        type_stats_query = """
            WITH pokemon_type_counts AS (
                SELECT name, COUNT(*) as type_count
                FROM pokemon_marts.scatter_pokemon_height_weight
                GROUP BY name
            )
            SELECT
                t.type_name as type_name,
                COUNT(*) as total_count,
                COUNTIF(st.type_count = 1) as single_type_count,
                ROUND(COUNTIF(st.type_count = 1) * 1.0 / COUNT(*), 3) as single_type_rate
            FROM
                pokemon_marts.scatter_pokemon_height_weight t
            JOIN
                pokemon_type_counts st ON t.name = st.name
            GROUP BY 1
        """
        type_data: dict[str, dict[str, str | int | float]] = {}
        for row in con.sql(type_stats_query).fetchall():
            type_data[row[0]] = {
                "type_name": row[0],
                "total_count": row[1],
                "single_type_count": row[2],
                "single_type_rate": row[3]
            }

        # 共起リンクの計算
        # t1.type_name < t2.type_nameとすることで逆のリンクを重複して計算しないようにする
        co_occurrence_query = """
            SELECT
                t1.type_name AS source,
                t2.type_name AS target,
                COUNT(*) as value
            FROM
                pokemon_marts.scatter_pokemon_height_weight t1
            JOIN
                pokemon_marts.scatter_pokemon_height_weight t2
                ON t1.name = t2.name AND t1.type_name < t2.type_name
            GROUP BY 1, 2
        """
        # タイプノード
        G: nx.Graph = nx.Graph()
        for type_name in type_data:
            G.add_node(type_name)

        co_links: list[CoLink] = []
        for row in con.sql(co_occurrence_query).fetchall():
            co_links.append({
                "source": row[0],
                "target": row[1],
                "value": row[2]
            })
            G.add_edge(row[0], row[1], weight=row[2])

        # ネットワーク指標の計算 (Centrality)
        # 次数中心性: どれだけ多くのタイプと組み合わせがあるか
        degree_cent: dict[str, float] = nx.degree_centrality(G)
        # 固有ベクトル中心性: よく組み合わされるタイプとどれだけ繋がっているか
        try:
            eigen_cent: dict[str, float] = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
        except:
            eigen_cent = {n: 0 for n in G.nodes()}

        # Community detection using NetworkX's greedy modularity algorithm
        communities: list[set[str]] = list(greedy_modularity_communities(G, weight='weight'))
        # Build a map from node to community index
        community_map: dict[str, int] = {}
        for idx, comm in enumerate(communities):
            for node in comm:
                community_map[node] = idx

        # ノードリストの構築 マージ
        nodes: list[TypeNodeStats] = []
        for type_name, stats in type_data.items():
            nodes.append({
                **stats,
                "degree_centrality": round(degree_cent.get(type_name, 0), 3),
                "eigenvector_centrality": round(eigen_cent.get(type_name, 0), 3),
                "group": 1,
                "community": community_map.get(type_name, -1) # Add community ID
            })

        # ポケモンノードと、ポケモン->タイプのリンク(bipartite_links)を取得
        pokemon_node_query = """
            SELECT
                name,
                array_agg(type_name) AS types
            FROM
                pokemon_marts.scatter_pokemon_height_weight
            GROUP BY
                name
        """
        pokemon_nodes: list[PokemonNode] = []
        bipartite_links: list[BipartiteLink] = []
        for row in con.sql(pokemon_node_query).fetchall():
            name, types = row[0], row[1]
            pokemon_nodes.append({
                "name": name,
                "types": types,
                "total_count": 1,
                "group": 2
            })
            for t in types:
                bipartite_links.append({"source": name, "target": t})

        output: NetworkOutput = {
            "type_nodes": nodes,
            "pokemon_nodes": pokemon_nodes,
            "co_links": co_links,
            "bipartite_links": bipartite_links
        }

        print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
