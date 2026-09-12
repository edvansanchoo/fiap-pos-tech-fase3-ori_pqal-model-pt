from db.connection import check_db_connection


def test_check_db_connection():
    assert check_db_connection() is True
