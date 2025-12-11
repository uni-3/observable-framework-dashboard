#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb==1.2.2",
# ]
# ///

# 実行権限必須
# chmod +x ./src/data/graph-analytics.json.py
# run by ./src/data/graph-analytics.json.py
import duckdb
import sys
import json

def main():
    try:
        # 未署名の拡張機能を許可して接続
        con = duckdb.connect(config={'allow_unsigned_extensions': 'true'})

        # DuckPGQのインストールとロード
        con.sql("INSTALL duckpgq FROM community;")
        con.sql("LOAD duckpgq;")

        # 公式サンプルデータのロード
        con.sql("CREATE TABLE Person AS SELECT * FROM 'https://gist.githubusercontent.com/Dtenwolde/2b02aebbed3c9638a06fda8ee0088a36/raw/8c4dc551f7344b12eaff2d1438c9da08649d00ec/person-sf0.003.csv';")
        con.sql("CREATE TABLE Person_knows_person AS SELECT * FROM 'https://gist.githubusercontent.com/Dtenwolde/81c32c9002d4059c2c3073dbca155275/raw/8b440e810a48dcaa08c07086e493ec0e2ec6b3cb/person_knows_person-sf0.003.csv';")

        # プロパティグラフの定義
        con.sql("""
            CREATE PROPERTY GRAPH snb
            VERTEX TABLES (
                Person
            )
            EDGE TABLES (
                Person_knows_person
                SOURCE KEY (Person1Id) REFERENCES Person (id)
                DESTINATION KEY (Person2Id) REFERENCES Person (id)
                LABEL knows
            );
        """)

        # グラフクエリの実行
        # 複雑なSQL（CTE+JSON）だとDuckDBが落ちるため、単純なクエリで結果を取得し
        # Python側でJSONを構築する方針に変更
        query = """
            SELECT
                source,
                target
            FROM GRAPH_TABLE (
                snb
                MATCH (a:Person)-[k:knows]->(b:Person)
                COLUMNS (a.firstName AS source, b.firstName AS target)
            )
            LIMIT 200;
        """

        # 結果を取得 (List of tuples)
        rows = con.sql(query).fetchall()

        # Python側で nodes, links を構築
        nodes_set = set()
        links = []

        for source, target in rows:
            if source and target: # NULLチェック
                nodes_set.add(source)
                nodes_set.add(target)
                links.append({"source": source, "target": target, "value": 1})

        # JSON構造を作成
        nodes = [{"id": name, "group": 1} for name in nodes_set]
        output = {"nodes": nodes, "links": links}

        # 出力
        print(json.dumps(output))

    except Exception as e:
        # エラーを標準エラー出力へ
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
