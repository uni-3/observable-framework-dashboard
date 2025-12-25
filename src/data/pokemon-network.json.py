#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb==1.2.1",
#     "python-dotenv",
#     "networkx",
# ]
# ///

import duckdb
import os
from dotenv import load_dotenv
import sys
import json
import networkx as nx

def main():
    try:
        load_dotenv(".env.local", override=True)

        database = os.getenv("DUCKDB_DATABASE")
        if not database:
            raise ValueError("DUCKDB_DATABASE environment variable is not set.")

        con = duckdb.connect(database, read_only=True)

        # 1. タイプの基本統計と単独率の計算
        # single_count: そのタイプ単体で存在するポケモンの数
        type_stats_query = """
            WITH pokemon_type_counts AS (
                SELECT name, count(*) as type_count
                FROM pokemon_marts.scatter_pokemon_height_weight
                GROUP BY name
            )
            SELECT
                t.type_name AS id,
                COUNT(*) as total_count,
                COUNT(CASE WHEN st.type_count = 1 THEN 1 END) as single_count,
                ROUND(COUNT(CASE WHEN st.type_count = 1 THEN 1 END) * 1.0 / COUNT(*), 3) as isolation_rate
            FROM
                pokemon_marts.scatter_pokemon_height_weight t
            JOIN
                pokemon_type_counts st ON t.name = st.name
            GROUP BY 1
        """
        type_data = {}
        for row in con.sql(type_stats_query).fetchall():
            type_data[row[0]] = {
                "id": row[0],
                "total_count": row[1],
                "single_count": row[2],
                "isolation_rate": row[3]
            }

        # 2. 共起リンクの計算
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
        co_links = []
        G = nx.Graph()
        # ノードを追加
        for tid in type_data:
            G.add_node(tid)

        for row in con.sql(co_occurrence_query).fetchall():
            co_links.append({
                "source": row[0],
                "target": row[1],
                "value": row[2]
            })
            G.add_edge(row[0], row[1], weight=row[2])

        # 3. ネットワーク指標の計算 (Centrality)
        # 次数中心性: どれだけ多くのタイプと組み合わせがあるか
        degree_cent = nx.degree_centrality(G)
        # 固有ベクトル中心性: 重要な（よく組み合わされる）タイプとどれだけ繋がっているか
        try:
            eigen_cent = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
        except:
            eigen_cent = {n: 0 for n in G.nodes()}

        # ノードリストの構築（指標をマージ）
        nodes = []
        for tid, stats in type_data.items():
            nodes.append({
                **stats,
                "degree_centrality": round(degree_cent.get(tid, 0), 3),
                "eigenvector_centrality": round(eigen_cent.get(tid, 0), 3),
                "group": 1
            })

        # 4. ポケモンノード (各ポケモンが持つタイプの配列込み)
        pokemon_node_query = """
            SELECT
                name AS id,
                array_agg(type_name) AS types
            FROM
                pokemon_marts.scatter_pokemon_height_weight
            GROUP BY
                name
        """
        pokemon_nodes = []
        for row in con.sql(pokemon_node_query).fetchall():
            pokemon_nodes.append({
                "id": row[0],
                "types": row[1],
                "total_count": 1,
                "group": 2
            })

        # 5. 二部グラフ用リンク (Pokemon -> Type)
        bipartite_query = """
            SELECT name, type_name FROM pokemon_marts.scatter_pokemon_height_weight
        """
        bipartite_links = []
        for row in con.sql(bipartite_query).fetchall():
            bipartite_links.append({"source": row[0], "target": row[1]})

        output = {
            "type_nodes": nodes,
            "pokemon_nodes": pokemon_nodes,
            "links": co_links,
            "bipartite_links": bipartite_links
        }

        print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
