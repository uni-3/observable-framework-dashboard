#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb==1.2.1",
#     "python-dotenv",
# ]
# ///

import os
from dotenv import load_dotenv
import duckdb

def main():
    load_dotenv(".env.local")
    load_dotenv(".env")

    database = os.getenv("DUCKDB_DATABASE")
    if not database:
        raise ValueError("DUCKDB_DATABASE environment variable is not set.")

    con = duckdb.connect(database, read_only=True)

    # クエリ実行
    res = con.sql("""
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
