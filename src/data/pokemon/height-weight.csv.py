#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb==1.5.2",
#     "python-dotenv",
# ]
# ///

import duckdb

from _ducklake import connect_pokemon_ducklake


def main() -> None:
    con: duckdb.DuckDBPyConnection = connect_pokemon_ducklake()

    # クエリ実行
    res: duckdb.DuckDBPyRelation = con.sql("""
        SELECT
            name,
            height,
            weight,
            string_agg(type_name, ',') AS type_names,
            min(type_name) AS type_name
        FROM pokemon_marts.scatter_pokemon_height_weight
        GROUP BY ALL
    """)

    # CSV形式で変数に取得
    res.write_csv("/dev/stdout", header=True)


if __name__ == "__main__":
    main()
