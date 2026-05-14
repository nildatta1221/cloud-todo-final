from flask import Flask, jsonify, request
from google import genai
import mysql.connector
import os
import time

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "rootpass")
DB_NAME = os.environ.get("DB_NAME", "tododb")


def get_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def init_db():
    for attempt in range(10):
        try:
            db = get_db()
            cur = db.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    what_to_do VARCHAR(255) NOT NULL,
                    due_date VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'not done'
                )
            """)

            db.commit()
            cur.close()
            db.close()
            print("Database initialized successfully")
            return

        except Exception as e:
            print("Waiting for MySQL to be ready...")
            print(e)
            time.sleep(5)

    raise Exception("Could not connect to MySQL after multiple attempts")


@app.route("/api/items", methods=["GET"])
def get_items():
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT what_to_do, due_date, status FROM entries")
    rows = cur.fetchall()

    cur.close()
    db.close()

    tdlist = [
        {
            "what_to_do": row[0],
            "due_date": row[1],
            "status": row[2]
        }
        for row in rows
    ]

    return jsonify(tdlist)


@app.route("/api/items", methods=["POST"])
def add_item():
    data = request.json

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "INSERT INTO entries (what_to_do, due_date, status) VALUES (%s, %s, %s)",
        (data["what_to_do"], data["due_date"], "not done")
    )

    db.commit()
    cur.close()
    db.close()

    return jsonify({"status": "ok"})


@app.route("/api/items/<item>", methods=["DELETE"])
def delete_item(item):
    db = get_db()
    cur = db.cursor()

    cur.execute(
        "DELETE FROM entries WHERE what_to_do=%s",
        (item,)
    )

    db.commit()
    cur.close()
    db.close()

    return jsonify({"status": "deleted"})


@app.route("/api/items/<item>", methods=["PUT"])
def mark_done(item):
    db = get_db()
    cur = db.cursor()

    cur.execute(
        "UPDATE entries SET status='done' WHERE what_to_do=%s",
        (item,)
    )

    db.commit()
    cur.close()
    db.close()

    return jsonify({"status": "updated"})


@app.route("/ai_suggest", methods=["POST"])
def ai_suggest():

    task = request.form["task"]

    try:
        resp = requests.post(
            TODO_API_URL + "/api/ai/suggest",
            json={"task": task},
            timeout=20
        )

        if resp.status_code == 200:
            data = resp.json()
            suggestion = data.get(
                "suggestion",
                "No suggestion returned."
            )
        else:
            suggestion = (
                f"AI service returned "
                f"{resp.status_code}"
            )

    except Exception as e:
        suggestion = f"AI unavailable: {str(e)}"

    resp = requests.get(TODO_API_URL + "/api/items")
    tdlist = resp.json()

    return render_template(
        "index.html",
        tdlist=tdlist,
        suggestion=suggestion
    )

if __name__ == "__main__":
    init_db()
    app.run("0.0.0.0", port=5001)