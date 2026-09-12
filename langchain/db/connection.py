import psycopg2
from config import DATABASE_URL


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def check_db_connection() -> bool:
    try:
        conn = get_connection()
        conn.close()
        return True
    except psycopg2.Error:
        return False
