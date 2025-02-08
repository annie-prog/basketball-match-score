"""
This module handles database interactions, including querying, inserting, and 
updating data in the PostgreSQL database.
"""

import psycopg2
from psycopg2.extensions import connection

def _get_connection() -> connection:
    """
    Establishes and returns a connection to the PostgreSQL database.
    """
    return psycopg2.connect(
        user='postgres',
        password='akonarch',
        host='localhost',
        port=5432,
        database='basketball_matches'
    )

def read_query(sql: str, sql_params: tuple = ()) -> list[tuple]:
    """
    Executes a read query on the database and returns the results.
    """
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, sql_params)
            return cursor.fetchall()

def insert_query(sql: str, sql_params: tuple = ()) -> int | None:
    """
    Executes an insert query on the database and returns the generated ID
    (if "RETURNING" is in the SQL query), or the last inserted ID.
    """
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, sql_params)
            conn.commit()

            if "RETURNING" in sql:
                return cursor.fetchone()[0]

            try:
                cursor.execute("SELECT LASTVAL();")
                lastval = cursor.fetchone()
                if lastval:
                    return lastval[0]
                return None
            except psycopg2.Error:
                return None

def update_query(sql: str, sql_params: tuple = ()) -> bool:
    """
    Executes an update query on the database and returns whether any rows were affected.
    """
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, sql_params)
            conn.commit()
            return cursor.rowcount > 0
