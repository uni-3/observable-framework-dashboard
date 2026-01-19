#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb==1.4.3",
#     "python-dotenv",
#     "pandas",
#     "scikit-learn",
#     "prince"
# ]
# ///

import duckdb
import os
from dotenv import load_dotenv
import sys
import json
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import prince

def main():
    try:
        # Determine the project root directory (3 levels up from this script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, "../../../"))

        load_dotenv(os.path.join(project_root, ".env.local"))
        load_dotenv(os.path.join(project_root, ".env"))

        database = os.getenv("DUCKDB_DATABASE")
        if not database:
             pass

        # If database is just a filename, assume it's in project root if not found
        if database and not os.path.isabs(database):
             possible_path = os.path.join(project_root, database)
             if os.path.exists(possible_path):
                 database = possible_path

        if not database:
             # Fallback
             possible_db = os.path.join(project_root, "dlt_data.duckdb")
             if os.path.exists(possible_db):
                 database = possible_db
             else:
                 raise ValueError(f"DUCKDB_DATABASE environment variable is not set and {possible_db} not found.")

        con = duckdb.connect(database, read_only=True)

        query = """
            SELECT
                habitat_name_ja,
                shape_name_ja,
                egg_groups_ja,
                list(type_name_ja) as types_ja,
                ja_name
            FROM
                pokemon_intermediate.pokemon_wide
            WHERE
                habitat_name_ja IS NOT NULL
                AND shape_name_ja IS NOT NULL
            GROUP BY
                habitat_name_ja,
                shape_name_ja,
                egg_groups_ja,
                ja_name
        """

        # Fetch data
        df = con.sql(query).df()

        # Preprocessing
        # 1. Indicator for Habitat (Categorical)
        habitat_dummies = pd.get_dummies(df['habitat_name_ja'], prefix='habitat')

        # 2. Indicator for Shape (Categorical)
        shape_dummies = pd.get_dummies(df['shape_name_ja'], prefix='shape')

        # 3. Indicator for Egg Groups (Multi-label)
        # egg_groups_ja is likely a list of strings due to DuckDB array -> Python list conversion
        mlb_egg = MultiLabelBinarizer()
        egg_dummies_matrix = mlb_egg.fit_transform(df['egg_groups_ja'])
        egg_dummies = pd.DataFrame(
            egg_dummies_matrix,
            columns=[f"egg_{c}" for c in mlb_egg.classes_],
            index=df.index
        )

        # 4. Indicator for Types (Multi-label)
        # Assuming types_ja is also an array. If it comes as list, usage is same as egg groups.
        mlb_type = MultiLabelBinarizer()
        type_dummies_matrix = mlb_type.fit_transform(df['types_ja'])
        type_dummies = pd.DataFrame(
            type_dummies_matrix,
            columns=[f"type_{c}" for c in mlb_type.classes_],
            index=df.index
        )

        # Combine all indicators
        # Note: Standard MCA usually takes a dataframe of categorical variables.
        # However, Prince's MCA supports categorical columns.
        # BUT since we have multi-label egg groups, it's intricate.
        # Prince MCA takes categories. If we flatten egg groups, we duplicate rows.
        # If we use indicator matrix directly, we should use CA (Simple Correspondence Analysis) on the Indicator Matrix?
        # MCA in prince takes a dataframe of categorical variables.

        # Strategy: Use CA on the manually constructed Indicator Matrix (Burt Matrix or Indicator Matrix).
        # Actually, MCA *is* CA on the indicator matrix.
        # So let's construct the full indicator matrix and run CA on it.

        indicator_matrix = pd.concat([habitat_dummies, shape_dummies, egg_dummies, type_dummies], axis=1).astype(float)

        # Prince CA
        ca = prince.CA(
            n_components=2,
            n_iter=10,
            copy=True,
            check_input=True,
            engine='sklearn',
            random_state=42
        )

        ca = ca.fit(indicator_matrix)

        # Row coordinates (Pokemon)
        row_coords = ca.row_coordinates(indicator_matrix)
        row_coords['name'] = df['ja_name']
        row_coords['type'] = 'pokemon'

        # Column coordinates (Categories)
        col_coords = ca.column_coordinates(indicator_matrix)
        col_coords['name'] = col_coords.index
        # Determine original type (habitat, shape, egg) based on prefix or known sets
        # We used prefixes 'habitat_', 'shape_', 'egg_'

        def get_category_type(col_name):
            if col_name.startswith('habitat_'): return 'habitat', col_name.replace('habitat_', '')
            if col_name.startswith('shape_'): return 'shape', col_name.replace('shape_', '')
            if col_name.startswith('egg_'): return 'egg', col_name.replace('egg_', '')
            if col_name.startswith('type_'): return 'poke_type', col_name.replace('type_', '') # use poke_type to avoid confusion with entity 'type' column
            return 'other', col_name

        col_types = [get_category_type(c) for c in col_coords.index]
        col_coords['type'] = [t[0] for t in col_types]
        col_coords['label'] = [t[1] for t in col_types]

        # Rename coordinate columns for consistency
        row_coords = row_coords.rename(columns={0: 'x', 1: 'y'})
        col_coords = col_coords.rename(columns={0: 'x', 1: 'y'})

        # Combine
        output_data = []

        # Add Pokemon points
        for _, row in row_coords.iterrows():
            output_data.append({
                "name": row['name'],
                "type": "pokemon",
                "x": row['x'],
                "y": row['y'],
                "label": row['name'] # Label for tooltip
            })

        # Add Category points
        for _, row in col_coords.iterrows():
            output_data.append({
                "name": row['name'], # Full feature name
                "type": row['type'],
                "x": row['x'],
                "y": row['y'],
                "label": row['label']
            })

        print(json.dumps(output_data, ensure_ascii=False))

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        # Print detailed traceback for debugging
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
