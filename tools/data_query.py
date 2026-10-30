"""Tools that read the challenge data in DATA_DIR (the judges swap in different data)."""
import csv
import io
import json
import os
import re
import sqlite3

import config
from tools import Tool


def _path(filename):
    path = os.path.join(config.DATA_DIR, os.path.basename(filename))
    if not os.path.exists(path):
        raise FileNotFoundError(f"{filename} not found. Use list_files first.")
    return path


class ListFiles(Tool):
    name = "list_files"
    description = "List the data files available for this task."
    args_doc = "{}"

    def execute(self):
        files = sorted(f for f in os.listdir(config.DATA_DIR) if not f.startswith(".") and f != "queries.json")
        return ", ".join(files) or "ERROR: no data files found"


class ReadFile(Tool):
    name = "read_file"
    description = "Read a CSV/JSON/text data file (first rows only if large)."
    args_doc = '{"filename": "scores.csv", "max_chars": 3000}'

    def execute(self, filename, max_chars=3000):
        with open(_path(filename), encoding="utf-8", errors="ignore") as f:
            text = f.read()
        if not text.strip():
            return f"ERROR: {filename} is empty"
        return text[:int(max_chars)]


class SqlQuery(Tool):
    name = "sql_query"
    description = ("Run a read-only SQL SELECT over a CSV file loaded as table `data` "
                   "(column names come from the CSV header).")
    args_doc = '{"filename": "transactions.csv", "sql": "SELECT merchant, SUM(amount) FROM data GROUP BY merchant"}'

    def execute(self, filename, sql):
        if not re.match(r"^\s*select\b", sql, re.I) or ";" in sql.strip().rstrip(";"):
            raise ValueError("only a single SELECT statement is allowed")
        with open(_path(filename), encoding="utf-8", errors="ignore") as f:
            rows = list(csv.reader(io.StringIO(f.read())))
        if len(rows) < 2:
            return f"ERROR: {filename} has no data rows"
        header = [re.sub(r"\W", "_", h.strip()) or f"c{i}" for i, h in enumerate(rows[0])]
        db = sqlite3.connect(":memory:")
        cols_sql = ", ".join('"%s" NUMERIC' % h for h in header)  # NUMERIC: "31" compares as a number
        db.execute("CREATE TABLE data (%s)" % cols_sql)
        db.executemany(f"INSERT INTO data VALUES ({','.join('?' * len(header))})", [r for r in rows[1:] if len(r) == len(header)])
        try:
            cur = db.execute(sql.strip().rstrip(";"))
            cols = [c[0] for c in cur.description]
            return json.dumps({"columns": cols, "rows": cur.fetchmany(50)}, default=str)
        finally:
            db.close()
