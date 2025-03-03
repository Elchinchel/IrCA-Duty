import sqlite3

from sqlalchemy.engine import Connection


NOCASE_COLLATION = 'CUSTOMNOCASE'


def _lowercase_coll_fn(a: str, b: str) -> int:
    a = a.lower()
    b = b.lower()
    if a == b:
        return 0
    if a > b:
        return 1
    return -1


def setup_collate_function(alchemy_conn: Connection):
    conn = alchemy_conn.connection.driver_connection
    assert isinstance(conn, sqlite3.Connection)

    conn.create_collation(NOCASE_COLLATION, _lowercase_coll_fn)
