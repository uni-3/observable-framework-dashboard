#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb==1.4.3",
#     "python-dotenv",
# ]
# ///

import duckdb
import os
from dotenv import load_dotenv
import sys
import json

def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, "../../../"))

        load_dotenv(os.path.join(project_root, ".env.local"))
        load_dotenv(os.path.join(project_root, ".env"))

        database = os.getenv("DUCKDB_DATABASE")
        if not database:
             # Fallback to local file if env not set
             possible_db = os.path.join(project_root, "dlt_data.duckdb")
             if os.path.exists(possible_db):
                 database = possible_db
             else:
                 raise ValueError("DUCKDB_DATABASE environment variable is not set and fallback not found.")

        con = duckdb.connect(database, read_only=True)

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

        results = []
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
