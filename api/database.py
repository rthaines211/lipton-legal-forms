"""
Database connection management using Psycopg 3
"""
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from contextlib import contextmanager
from typing import Generator
import logging

from api.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global connection pool
_pool: ConnectionPool | None = None


def init_db_pool() -> ConnectionPool:
    """
    Initialize the database connection pool

    Returns:
        ConnectionPool: Configured psycopg connection pool
    """
    global _pool

    if _pool is None:
        logger.info(f"Initializing database pool: {settings.database_url}")
        _pool = ConnectionPool(
            conninfo=settings.database_url,
            min_size=settings.database_pool_min_size,
            max_size=settings.database_pool_max_size,
            kwargs={
                "row_factory": dict_row,
                "autocommit": False,
            },
        )
        logger.info("Database pool initialized successfully")

    return _pool


def close_db_pool():
    """Close the database connection pool"""
    global _pool

    if _pool:
        logger.info("Closing database pool")
        _pool.close()
        _pool = None


@contextmanager
def get_db_connection() -> Generator[psycopg.Connection, None, None]:
    """
    Get a database connection from the pool

    Yields:
        psycopg.Connection: Database connection with dict_row factory

    Example:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cases")
                results = cur.fetchall()
    """
    pool = init_db_pool()

    with pool.connection() as conn:
        try:
            yield conn
        except Exception as e:
            logger.error(f"Database error: {e}")
            conn.rollback()
            raise
        else:
            conn.commit()


@contextmanager
def get_db_cursor(connection: psycopg.Connection | None = None) -> Generator[psycopg.Cursor, None, None]:
    """
    Get a database cursor, optionally from a provided connection

    Args:
        connection: Optional existing connection. If None, creates new connection from pool

    Yields:
        psycopg.Cursor: Database cursor

    Example:
        # With automatic connection
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM cases")

        # With existing connection (for transactions)
        with get_db_connection() as conn:
            with get_db_cursor(conn) as cur:
                cur.execute("INSERT INTO cases ...")
    """
    if connection:
        with connection.cursor() as cursor:
            yield cursor
    else:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                yield cursor


def execute_query(query: str, params: dict | tuple | None = None) -> list[dict]:
    """
    Execute a SELECT query and return results

    Args:
        query: SQL query string
        params: Query parameters (dict or tuple)

    Returns:
        list[dict]: Query results as list of dictionaries
    """
    with get_db_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def execute_insert(query: str, params: dict | tuple | None = None) -> dict | None:
    """
    Execute an INSERT query with RETURNING clause

    Args:
        query: SQL INSERT query with RETURNING clause
        params: Query parameters

    Returns:
        dict | None: Inserted row data or None
    """
    with get_db_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()


def execute_update(query: str, params: dict | tuple | None = None) -> int:
    """
    Execute an UPDATE or DELETE query

    Args:
        query: SQL UPDATE or DELETE query
        params: Query parameters

    Returns:
        int: Number of affected rows
    """
    with get_db_cursor() as cur:
        cur.execute(query, params)
        return cur.rowcount
