"""
DBShield SQL Guardrail & Cursor Wrapper Example (SQLite + LangChain Wrapper)
Run: python examples/sqlite_guard_example.py
"""

import sqlite3

from dbshield.guard import DBShieldGuard, DBShieldSecurityViolation
from dbshield.integrations.langchain import DBShieldSQLDatabase
from dbshield.middleware import DBShieldCursorWrapper


class _SqliteAdapter:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def run(self, command: str) -> list:
        return self._conn.execute(command).fetchall()


def main() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
    conn.execute("INSERT INTO users (id, email) VALUES (1, 'alice@example.com')")

    guard = DBShieldGuard(safety_tier="BALANCED")
    cursor = DBShieldCursorWrapper(conn.cursor(), guard)
    print("Allowed SELECT:", cursor.execute("SELECT id, email FROM users WHERE id = 1").fetchall())

    wrapped_db = DBShieldSQLDatabase(_SqliteAdapter(conn), safety_tier="STRICT")
    try:
        wrapped_db.run("DROP TABLE users")
    except DBShieldSecurityViolation as err:
        print("Blocked dangerous DDL:", err)


if __name__ == "__main__":
    main()
