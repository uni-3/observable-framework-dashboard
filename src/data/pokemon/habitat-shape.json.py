#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb==1.5.2",
#     "python-dotenv",
# ]
# ///

import duckdb
import sys
import json
from typing import TypedDict

from _ducklake import connect_pokemon_ducklake


class HabitatShapeOutput(TypedDict):
    """生息地・形状データの出力型定義"""
    habitat_name: str
    habitat_name_ja: str
    shape_name: str
    shape_name_ja: str
    egg_groups: list[str]
    egg_groups_ja: list[str]
    types: list[str]
    types_ja: list[str]
    name: str
    ja_name: str
    generation_name_ja: str


def main() -> None:
    try:
        con: duckdb.DuckDBPyConnection = connect_pokemon_ducklake()

        query = """
            SELECT
                COALESCE(habitat_name, 'unknown') as habitat_name,
                COALESCE(habitat_name_ja, '不明') as habitat_name_ja,
                shape_name,
                shape_name_ja,
                egg_groups,
                egg_groups_ja,
                list(type_name) as types,
                list(type_name_ja) as types_ja,
                name,
                ja_name,
                generation_name_ja
            FROM
                pokemon_intermediate.pokemon_wide
            WHERE
                shape_name IS NOT NULL
            GROUP BY
                habitat_name,
                habitat_name_ja,
                shape_name,
                shape_name_ja,
                egg_groups,
                egg_groups_ja,
                name,
                ja_name,
                generation_name_ja
        """

        results: list[HabitatShapeOutput] = []
        for row in con.sql(query).fetchall():
            results.append({
                "habitat_name": row[0],
                "habitat_name_ja": row[1],
                "shape_name": row[2],
                "shape_name_ja": row[3],
                "egg_groups": row[4],
                "egg_groups_ja": row[5],
                "types": row[6],
                "types_ja": row[7],
                "name": row[8],
                "ja_name": row[9],
                "generation_name_ja": row[10]
            })

        print(json.dumps(results, ensure_ascii=False))

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
