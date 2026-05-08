import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv


REQUIRED_ENV_VARS = (
    "DUCKLAKE_POSTGRES_DSN",
    "DUCKLAKE_DATA_PATH",
    "R2_ACCOUNT_ID",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} environment variable is not set.")
    return value


def connect_pokemon_ducklake() -> duckdb.DuckDBPyConnection:
    project_root = _project_root()
    load_dotenv(project_root / ".env.local")
    load_dotenv(project_root / ".env")

    env = {name: _required_env(name) for name in REQUIRED_ENV_VARS}

    con = duckdb.connect(":memory:")
    con.sql("INSTALL ducklake")
    con.sql("LOAD ducklake")
    con.sql("INSTALL postgres")
    con.sql("LOAD postgres")
    con.sql("INSTALL httpfs")
    con.sql("LOAD httpfs")
    con.sql(f"""
        CREATE OR REPLACE SECRET pokemon_r2 (
            TYPE r2,
            KEY_ID {_sql_string(env["R2_ACCESS_KEY_ID"])},
            SECRET {_sql_string(env["R2_SECRET_ACCESS_KEY"])},
            ACCOUNT_ID {_sql_string(env["R2_ACCOUNT_ID"])}
        )
    """)
    con.sql(f"""
        ATTACH {_sql_string("ducklake:postgres:" + env["DUCKLAKE_POSTGRES_DSN"])} AS pokemon (
            DATA_PATH {_sql_string(env["DUCKLAKE_DATA_PATH"])},
            READ_ONLY,
            CREATE_IF_NOT_EXISTS false
        )
    """)
    con.sql("USE pokemon")
    return con
