# -----------USERS--------------
SQL_GET_ALL_USERS = """
SELECT *
FROM users
"""
SQL_GET_USER_BY_ID = """
SELECT *
FROM users
WHERE id=?
"""
SQL_GET_USER_BY_USERNAME = """
SELECT *
FROM users
WHERE username=?
"""
SQL_INSERT_USER = """
INSERT INTO users (username, password)
VALUES (?,?)
"""
SQL_UPDATE_USER = """
UPDATE users
SET username=?, password=?
WHERE id=?
"""

SQL_DELETE_USER = """
DELETE FROM users
WHERE id=?
"""

# -----------EXPENSES--------------
SQL_GET_ALL_EXPENSES = """
SELECT *
FROM expenses
"""
SQL_GET_EXPENSES_BY_ID = """
SELECT *
FROM expenses
WHERE id=?
"""
SQL_INSERT_EXPENSE = """
INSERT INTO expenses (title, description, amount, date, category, user_id)
VALUES (?, ?, ?, ?, ?, ?)
"""
SQL_UPDATE_EXPENSE = """
UPDATE expenses 
SET title = ?, description = ?, amount = ?, date = ?, category = ?, user_id = ?
WHERE id = ?
"""
SQL_DELETE_EXPENSE = """
DELETE FROM expenses
WHERE id=?
"""
SQL_GET_EXPENSES_BY_USER_ID = """
SELECT *
FROM expenses
WHERE user_id = ?
"""