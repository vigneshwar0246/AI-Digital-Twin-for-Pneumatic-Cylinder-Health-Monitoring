"""Small thread-safe SQLite prediction repository."""
import json
import sqlite3
from pathlib import Path


class PredictionRepository:
    def __init__(self, path):
        self.path = str(path)

    def _connect(self):
        connection = sqlite3.connect(self.path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL, raw_sensors TEXT NOT NULL,
                predicted_fault TEXT NOT NULL, confidence REAL NOT NULL,
                probabilities TEXT NOT NULL, estimated_health REAL,
                estimated_rul REAL, warmup INTEGER NOT NULL, control TEXT NOT NULL)""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_predictions_session ON predictions(session_id, id)")

    def add(self, item):
        with self._connect() as db:
            cur = db.execute("""INSERT INTO predictions
                (timestamp,session_id,raw_sensors,predicted_fault,confidence,probabilities,estimated_health,estimated_rul,warmup,control)
                VALUES (?,?,?,?,?,?,?,?,?,?)""", (
                item["timestamp"], item["session_id"], json.dumps(item["reading"]), item["fault"],
                item["confidence"], json.dumps(item["probabilities"]), item["health"], item["rul"]["estimated_remaining_cycles"],
                int(item["warmup"]), json.dumps(item["control"])))
            return cur.lastrowid

    def history(self, session_id=None, limit=100):
        query = "SELECT * FROM predictions"
        args = []
        if session_id:
            query += " WHERE session_id=?"; args.append(session_id)
        query += " ORDER BY id DESC LIMIT ?"; args.append(limit)
        with self._connect() as db:
            rows = db.execute(query, args).fetchall()
        result = []
        for row in rows:
            value = dict(row)
            for key in ("raw_sensors", "probabilities", "control"):
                value[key] = json.loads(value[key])
            value["warmup"] = bool(value["warmup"])
            result.append(value)
        return result

    def ping(self):
        try:
            with self._connect() as db: db.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False
