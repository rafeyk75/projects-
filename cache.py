from __future__ import annotations
import sqlite3, json, time, pathlib
from typing import Any, Optional

DEFAULT_TTL = 2 * 60 * 60  # 2 hours

class Cache:
    def __init__(self, path: str | pathlib.Path = ".weather_cache.sqlite") -> None:
        self.path = str(path)
        self._ensure()

    def _ensure(self) -> None:
        con = sqlite3.connect(self.path)
        with con:
            con.execute("""
            CREATE TABLE IF NOT EXISTS kv (
                k TEXT PRIMARY KEY,
                v TEXT NOT NULL,
                ts INTEGER NOT NULL
            )
            """)
        con.close()

    def get(self, key: str, ttl: int = DEFAULT_TTL) -> Optional[dict]:
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT v, ts FROM kv WHERE k=?", (key,))
        row = cur.fetchone()
        con.close()
        if not row:
            return None
        v_json, ts = row
        if time.time() - ts > ttl:
            return None
        return json.loads(v_json)

    def set(self, key: str, value: dict) -> None:
        con = sqlite3.connect(self.path)
        with con:
            con.execute("REPLACE INTO kv (k, v, ts) VALUES (?, ?, ?)",
                        (key, json.dumps(value), int(time.time())))
        con.close()
