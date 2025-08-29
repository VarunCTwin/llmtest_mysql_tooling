from typing import List, Any, Dict
import mysql.connector
from ..config import MYSQL

def run_sql_query(query: str, database: str = None) -> List[tuple[Any, ...]]:
    """Run SQL query against a specific database or the default one."""
    target_db = database or MYSQL.database
    conn = mysql.connector.connect(
        host=MYSQL.host,
        port=MYSQL.port,
        user=MYSQL.user,
        password=MYSQL.password,
        database=target_db,
    )
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return rows
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()

def run_sql_query_multi_db(query: str) -> Dict[str, List[tuple[Any, ...]]]:
    """Run SQL query against all configured databases."""
    results = {}
    for db in MYSQL.databases:
        try:
            results[db] = run_sql_query(query, db)
        except Exception as e:
            results[db] = f"Error: {e}"
    return results
