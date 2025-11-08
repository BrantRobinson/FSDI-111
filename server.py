from flask import Flask, jsonify, request
import sqlite3 

app = Flask(__name__)

DB_NAME = "budget_manager.db"

def init_db():
    conn = sqlite3.connect(DB_NAME) # opens a connection to the db filed named budget_manager.db 
    cursor = conn.cursor() # creates a cursor/tool that lets us send commands (INSERT, SELECT, ...)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit() # save changes to the db
    conn.close() #close the connection to the db


@app.post("/api/register")
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "User successfully registered"
    }), 201

@app.post("/api/login")
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and user["password"] == password:
        return jsonify({
        "success": True,
        "message": "Login successful",
        "user_id": user["id"],
        "username": user["username"],
    }), 200

    return jsonify({
        "success": False,
        "message": "Invalid Credentials"
    }), 401 #UNAUTHORIZED


@app.get("/api/users/<int:user_id>")
def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "success": True,
            "message": "User found",
            "user_id": user["id"],
            "username": user["username"]
        }), 201
    
    return jsonify({
        "success": False,
        "message": "User not found",
    }), 404

    
    

@app.get("/api/health")
def health_check():
    return jsonify({
        "status": "OK"
    }), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
