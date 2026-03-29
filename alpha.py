from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, hashlib, os, requests, re, datetime as dt

app = Flask(__name__)
CORS(app)
DB = "users.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS usage(uid TEXT PRIMARY KEY, counter INT);")

def uid(ip):
    return hashlib.md5(ip.encode()).hexdigest()[:10]

@app.route("/api/copy", methods=["POST"])
def api():
    ip = request.headers.get("X-Forwarded-For", "0.0.0.0").split(",")[0]
    uid_ = uid(ip)
    with sqlite3.connect(DB) as conn:
        cur = conn.execute("SELECT counter FROM usage WHERE uid=?", (uid_,))
        row = cur.fetchone()
        used = row[0] if row else 0
    if used >= 5:
        return jsonify({"copy": None, "payUrl": "https://pagar.me/...sandbox-checkout..."})
    # chama IA de graça (ex.: HuggingFace Inference API sem token)
    store = request.json.get("store", "minha loja")
    copy = f"🎁 {store} liberou 10% OFF só hoje! Corre que é por tempo limitado."
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT OR IGNORE INTO usage(uid,counter) VALUES(?,0)", (uid_,))
        conn.execute("UPDATE usage SET counter=counter+1 WHERE uid=?", (uid_,))
    return jsonify({"copy": copy, "left": 4 - used})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
