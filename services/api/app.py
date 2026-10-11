import os
import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, request


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
    app.config["DATABASE"] = os.environ.get(
        "DATABASE_PATH",
        str(Path(__file__).parent / "items.db"),
    )

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"], timeout=10)
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with app.app_context():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 100)
            )
            """
        )
        db.commit()

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.get("/api/items")
    def list_items():
        rows = get_db().execute("SELECT id, name FROM items ORDER BY id").fetchall()
        return jsonify(items=[dict(row) for row in rows]), 200

    @app.post("/api/items")
    def create_item():
        if not request.is_json:
            return jsonify(error="Content-Type doit etre application/json"), 415

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify(error="Un objet JSON valide est requis"), 400

        if set(data) != {"name"}:
            return jsonify(error="Le seul champ attendu est name"), 400

        name = data["name"]

        if not isinstance(name, str):
            return jsonify(error="name doit etre une chaine de caracteres"), 400

        name = name.strip()

        if not 1 <= len(name) <= 100:
            return jsonify(error="name doit contenir entre 1 et 100 caracteres"), 400

        db = get_db()
        cursor = db.execute(
            "INSERT INTO items (name) VALUES (?)",
            (name,),
        )
        db.commit()

        return jsonify(id=cursor.lastrowid, name=name), 201

    @app.errorhandler(413)
    def body_too_large(error):
        return jsonify(error="Corps de requete trop volumineux"), 413

    return app
