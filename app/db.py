import sqlite3
import time

from . import config


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users(
               user_id INTEGER PRIMARY KEY,
               username TEXT,
               first_seen INTEGER
           )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS history(
               user_id INTEGER,
               role TEXT,
               content TEXT,
               ts INTEGER
           )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS requests(
               user_id INTEGER,
               day TEXT,
               count INTEGER,
               PRIMARY KEY(user_id, day)
           )"""
    )
    return conn


_CONN = _connect()


def register_user(user_id: int, username: str) -> None:
    _CONN.execute(
        "INSERT OR IGNORE INTO users VALUES(?, ?, ?)",
        (user_id, username, int(time.time())),
    )
    _CONN.commit()


def add_message(user_id: int, role: str, content: str) -> None:
    _CONN.execute(
        "INSERT INTO history VALUES(?, ?, ?, ?)",
        (user_id, role, content, int(time.time())),
    )
    _CONN.commit()


def get_history(user_id: int, limit: int = 12) -> list[dict]:
    rows = _CONN.execute(
        "SELECT role, content FROM ("
        "  SELECT role, content, ts FROM history WHERE user_id = ?"
        "  ORDER BY ts DESC LIMIT ?"
        ") ORDER BY ts ASC",
        (user_id, limit),
    ).fetchall()
    return [{"role": r, "content": c} for r, c in rows]


def clear_history(user_id: int) -> None:
    _CONN.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
    _CONN.commit()


def check_rate_limit(user_id: int) -> bool:
    day = time.strftime("%Y-%m-%d")
    row = _CONN.execute(
        "SELECT count FROM requests WHERE user_id = ? AND day = ?",
        (user_id, day),
    ).fetchone()
    count = row[0] if row else 0
    if count >= config.MAX_REQUESTS_PER_DAY:
        return False
    _CONN.execute(
        "INSERT INTO requests VALUES(?, ?, ?) "
        "ON CONFLICT(user_id, day) DO UPDATE SET count = count + 1",
        (user_id, day, 1),
    )
    _CONN.commit()
    return True


def stats() -> dict:
    users = _CONN.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    msgs = _CONN.execute(
        "SELECT COUNT(*) FROM history WHERE ts > ?",
        (int(time.time()) - 86400,),
    ).fetchone()[0]
    return {"users": users, "messages_24h": msgs}
