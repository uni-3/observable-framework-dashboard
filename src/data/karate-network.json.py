#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb==1.2.2",
# ]
# ///

# 実行権限必須
# chmod +x ./src/data/karate-network.json.py
# run by ./src/data/karate-network.json.py
import duckdb
import sys
import json

def main():
    try:
        # unsigned extension for install duckpgq
        con = duckdb.connect(config={'allow_unsigned_extensions': 'true'})

        # DuckPGQとhttpfsのインストールとロード
        con.sql("INSTALL duckpgq FROM community;")
        con.sql("INSTALL httpfs;")
        con.sql("LOAD duckpgq;")
        con.sql("LOAD httpfs;")

        # Karate Club データのロード (Edges)
        con.sql("CREATE TABLE Edges AS SELECT column0 AS source_id, column1 AS target_id FROM read_csv_auto('https://raw.githubusercontent.com/raphaelgodro/Kernighan-Lin/master/karate-network.csv');")

        # Nodes テーブルの生成 (EdgesからユニークなIDを抽出)
        con.sql("CREATE TABLE Nodes AS SELECT DISTINCT source_id AS id, cast(id as VARCHAR) as name FROM Edges UNION SELECT DISTINCT target_id AS id, cast(id as VARCHAR) as name FROM Edges;")

        # プロパティグラフの定義
        con.sql("""
            CREATE PROPERTY GRAPH karate_club
            VERTEX TABLES (
                Nodes
            )
            EDGE TABLES (
                Edges
                SOURCE KEY (source_id) REFERENCES Nodes (id)
                DESTINATION KEY (target_id) REFERENCES Nodes (id)
                LABEL connects
            );
        """)

        # 全エッジを取得
        query = """
            SELECT
                source,
                target
            FROM GRAPH_TABLE (
                karate_club
                MATCH (a:Nodes)-[e:connects]->(b:Nodes)
                COLUMNS (a.name AS source, b.name AS target)
            )
        """

        # 結果を取得
        rows = con.sql(query).fetchall()

        # d3用の nodes, links を構築
        nodes_set = set()
        links = []
        for source, target in rows:
            if source and target: # NULLチェック
                nodes_set.add(source)
                nodes_set.add(target)
                links.append({"source": source, "target": target, "value": 1})

        nodes = [{"id": name, "group": 1} for name in nodes_set]
        output = {"nodes": nodes, "links": links}

        # 出力
        print(json.dumps(output))

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
