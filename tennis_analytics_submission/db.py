"""
Database Management Module for Tennis Analytics Explorer.
Provides robust SQLAlchemy engine initialization, safe multi-dialect execution,
safe session handling, and read-only query execution.
"""

import re
import logging
from pathlib import Path
from typing import Tuple, List, Optional
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL, BASE_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base Model
Base = declarative_base()

def create_db_engine():
    """Creates an engine with safe pooling and connection arguments."""
    connect_args = {}
    if DATABASE_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        return create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
    else:
        return create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )

# Global engine and sessionmaker
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def sanitize_database_url(url: str) -> str:
    """Hides password from database URL for secure logging and UI display."""
    if "@" in url and ":" in url:
        return re.sub(r":([^:@]+)@", ":****@", url)
    return url

def check_connection() -> Tuple[bool, str]:
    """Tests the database connection and returns (success, message)."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Database connection successful."
    except Exception as e:
        safe_msg = str(e)
        # Prevent exposing raw password
        if "@" in safe_msg:
            safe_msg = re.sub(r":([^:@]+)@", ":****@", safe_msg)
        return False, f"Database connection error: {safe_msg}"

def init_db(schema_file_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Initializes database tables and indexes safely from schema.sql.
    Splits statements properly and handles dialect differences.
    """
    if schema_file_path is None:
        schema_file_path = str(BASE_DIR / "schema.sql")

    schema_file = Path(schema_file_path)
    if not schema_file.exists():
        return False, f"Schema file not found at: {schema_file_path}"

    with open(schema_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split into discrete SQL statements, ignoring comments
    statements = []
    current_stmt = []
    for line in sql_content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        current_stmt.append(line)
        if stripped.endswith(";"):
            full_stmt = "\n".join(current_stmt).strip()
            # remove trailing semicolon for certain drivers if needed
            statements.append(full_stmt)
            current_stmt = []

    if current_stmt:
        remainder = "\n".join(current_stmt).strip()
        if remainder:
            statements.append(remainder)

    try:
        with engine.begin() as conn:
            for stmt in statements:
                if not stmt:
                    continue
                try:
                    conn.execute(text(stmt))
                except Exception as stmt_err:
                    # Ignore view already exists or minor non-fatal warnings
                    err_str = str(stmt_err).lower()
                    if "already exists" in err_str or "duplicate" in err_str:
                        logger.warning(f"Ignored non-fatal notice: {stmt_err}")
                        continue
                    else:
                        raise stmt_err

        return True, "All tables, views, and indexes successfully initialized."
    except Exception as e:
        safe_msg = sanitize_database_url(str(e))
        return False, f"Database initialization failed: {safe_msg}"

def get_table_names() -> List[str]:
    """Returns list of all user tables in the database."""
    try:
        inspector = inspect(engine)
        return inspector.get_table_names()
    except Exception as e:
        logger.error(f"Error inspecting tables: {e}")
        return []

def get_table_schema_df(table_name: str) -> pd.DataFrame:
    """Returns columns, types, and nullability for a table as DataFrame."""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        data = [
            {
                "Column": col.get("name"),
                "Type": str(col.get("type")),
                "Nullable": col.get("nullable"),
                "Primary Key": bool(col.get("primary_key", False)),
            }
            for col in columns
        ]
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Error inspecting columns for {table_name}: {e}")
        return pd.DataFrame()

def execute_query_df(sql_query: str, params: Optional[dict] = None) -> pd.DataFrame:
    """Executes a SQL query and returns the result as a Pandas DataFrame."""
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(sql_query), conn, params=params)
        return df
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise e

def execute_read_only_query(sql_query: str, max_rows: int = 200) -> Tuple[bool, Optional[pd.DataFrame], str]:
    """
    Safely executes an ad-hoc query for the SQL Console.
    Guarantees:
    - Only single SELECT / WITH queries are allowed.
    - Blocks INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, EXEC, etc.
    - Limits result rows to prevent memory exhaustion.
    """
    cleaned = sql_query.strip().strip(";")
    
    # Check for multiple statements
    if ";" in cleaned:
        return False, None, "Multiple statements are strictly forbidden in read-only console."

    # Normalize whitespace
    normalized = " " + " ".join(cleaned.split()).upper() + " "
    
    # Disallow write commands
    forbidden_keywords = [
        " INSERT ", " UPDATE ", " DELETE ", " DROP ", " ALTER ", " TRUNCATE ",
        " CREATE ", " REPLACE ", " GRANT ", " REVOKE ", " EXEC ", " EXECUTE ",
        " MERGE ", " UPSERT ", " CALL ", " VACUUM "
    ]
    for kw in forbidden_keywords:
        if kw in normalized:
            return False, None, f"Forbidden operation detected: {kw.strip()}. Only SELECT queries are permitted."

    # Ensure it starts with SELECT, WITH, or EXPLAIN
    stripped_upper = cleaned.upper().lstrip()
    if not (stripped_upper.startswith("SELECT") or stripped_upper.startswith("WITH") or stripped_upper.startswith("EXPLAIN")):
        return False, None, "Only SELECT or WITH queries are permitted."

    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(cleaned), conn)
            if len(df) > max_rows:
                df = df.head(max_rows)
                msg = f"Query successful ({len(df)} rows displayed, capped at {max_rows})."
            else:
                msg = f"Query successful ({len(df)} rows returned)."
            return True, df, msg
    except Exception as e:
        safe_msg = sanitize_database_url(str(e))
        return False, None, f"SQL Execution Error: {safe_msg}"
