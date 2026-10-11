import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/api/search")
def search():
    q = request.args.get("q", "")
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE items (name TEXT)")
    rows = conn.execute(f"SELECT name FROM items WHERE name LIKE '%{q}%'").fetchall()
    return jsonify(rows)
