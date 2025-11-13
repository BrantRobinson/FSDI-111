from flask import Flask, jsonify, request
import sqlite3 
from datetime import date
from response import success_response, not_found
from constants import SQL_GET_ALL_USERS, SQL_DELETE_USER, SQL_GET_USER_BY_ID, SQL_INSERT_USER, SQL_UPDATE_USER, SQL_GET_ALL_EXPENSES, SQL_GET_EXPENSES_BY_ID, SQL_INSERT_EXPENSE, SQL_GET_EXPENSES_AND_USERNAME_BY_USER_ID, SQL_DELETE_EXPENSE, SQL_UPDATE_EXPENSE, SQL_GET_USER_BY_USERNAME

app = Flask(__name__)

DB_NAME = "budget_manager.db"

def init_db():
    conn = sqlite3.connect(DB_NAME) # opens a connection to the db filed named budget_manager.db 
    cursor = conn.cursor() # creates a cursor/tool that lets us send commands (INSERT, SELECT, ...)
    
    # ------- users table --------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # ------- users table --------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        amount TEXT NOT NULL,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit() # save changes to the db
    conn.close() #close the connection to the db

# register user
@app.post("/api/register")
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(SQL_INSERT_USER, (username, password))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "User successfully registered"
    }), 201

# user login
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

# get user by id
@app.get("/api/users/<int:user_id>")
def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(SQL_GET_USER_BY_ID, (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return success_response("User Found", dict(user))
    
    return not_found("User")

# get all users
@app.get("/api/users")
def get_users():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(SQL_GET_ALL_USERS)
    rows = cursor.fetchall()
    conn.close()

    users = []

    for row in rows:
        user = {
            "id": row["id"],
            "username": row["username"],
            "password": row["password"]
        }
        users.append(user)

    return success_response("Users retrieved successfully", users)

# update users
@app.put("/api/users/<int:user_id>")
def update_user(user_id):

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(SQL_GET_USER_BY_ID, (user_id,))
    if not cursor.fetchone():
        conn.close()
        return not_found("User")
    
     # check if the username already exists (and isn't this user)
    cursor.execute(SQL_GET_USER_BY_USERNAME, (username,))
    row = cursor.fetchone()
    if row and row["id"] != user_id:
        conn.close()
        return jsonify(({
            "success": False,
            "message": "That username already exists"
        }))

    cursor.execute(SQL_UPDATE_USER, (username, password, user_id))
    conn.commit()
    conn.close()

    return success_response("The user was successfully updated", username)

@app.delete("/api/users/<int:user_id>")
def delete_users(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(SQL_GET_USER_BY_ID, (user_id,))
    if not cursor.fetchone():
        conn.close()
        return not_found("User")

    cursor.execute(SQL_DELETE_USER, (user_id,))
    conn.commit()
    conn.close()

    return success_response("User Deleted Successfully")

# -------  Expenses -----------

# Get all expenses
@app.get("/api/expenses")
def get_expenses():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(SQL_GET_ALL_EXPENSES)
    rows = cursor.fetchall()
    conn.close()

    expenses = []
    for row in rows:
        expense = {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "amount": row["amount"],
            "date": row["date"],
            "category": row["category"],
            "user_id": row["user_id"]
        }
        expenses.append(expense)

    return jsonify({
        "success": True,
        "message": "Expenses retrieved successfully",
        "data": expenses
    }), 200

# Get an expense by ID
@app.get("/api/expenses/<int:expense_id>")
def get_expense_by_id(expense_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(SQL_GET_EXPENSES_BY_ID, (expense_id,))
    expense = cursor.fetchone()
    conn.close()

    if not expense:
        return not_found("Expense")

    return jsonify({
        "success": True,
        "message": "Expense found",
        "data": {
            "id": expense["id"],
            "title": expense["title"],
            "description": expense["description"],
            "amount": expense["amount"],
            "date": expense["date"],
            "category": expense["category"],
            "user_id": expense["user_id"]
        }
    }), 200

# Create a new expense 
@app.post("/api/expenses")
def create_expense():
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    today = date.today()
    category = data.get("category")
    user_id = data.get("user_id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # check to see if the user id exists before allowing the post
    cursor.execute(SQL_GET_USER_BY_ID, (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({
            "success": False,
            "message": "User ID does not exist"
        }), 400   
    
    cursor.execute(SQL_INSERT_EXPENSE, (title, description, amount, today, category, user_id))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense created successfully"
    }), 201


# Update an expense by expense ID
@app.put("/api/expenses/<int:expense_id>")
def update_expense(expense_id):
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    category = data.get("category")
    user_id = data.get("user_id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(SQL_GET_EXPENSES_BY_ID, (expense_id,))
    if not cursor.fetchone():
        conn.close()
        return not_found("Expense")

    cursor.execute(SQL_UPDATE_EXPENSE, (title, description, amount, date, category, user_id, expense_id))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense successfully updated"
    }), 200

# Get all expenses for a certain user by user ID
@app.get("/api/users/<int:user_id>/expenses")
def get_expenses_by_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(SQL_GET_EXPENSES_AND_USERNAME_BY_USER_ID, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return not_found("Expense for that user")

    expenses = []
    for row in rows:
        expenses.append({
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "amount": row["amount"],
            "date": row["date"],
            "category": row["category"],
            "username": row["username"] 
        })

    return jsonify({
        "success": True,
        "message": "Expenses retrieved successfully",
        "data": expenses
    }), 200

# Delete an expense by expense ID
@app.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(SQL_GET_EXPENSES_BY_ID, (expense_id,))
    if not cursor.fetchone():
        conn.close()
        return not_found("Expense")

    cursor.execute(SQL_DELETE_EXPENSE, (expense_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense successfully deleted"
    }), 200

@app.get("/api/health")
def health_check():
    return jsonify({
        "status": "OK"
    }), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
