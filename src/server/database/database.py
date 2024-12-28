import sqlite3
import hashlib

class Database:
    def __init__(self, db_name="database/users.db"):
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the database with a users table."""
        with sqlite3.connect(self.db_name) as conn:
            # using cursor to execute SQL commands such as CREATE, INSERT, DELETE, etc:
            cursor = conn.cursor()
            # using execute() builtin-method to execute the SQL command:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
                """
            )
            # using commit() to save the changes:
            conn.commit()

    def _hash_password(self, password):
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, password):
        """Add a new user to the database."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                hashed_password = self._hash_password(password)
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password),
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_user(self, username, password):
        """Delete a user from the database if the password is correct."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            hashed_password = self._hash_password(password)
            cursor.execute(
                "DELETE FROM users WHERE username = ? AND password = ?",
                (username, hashed_password),
            )
            conn.commit()
            # return true if a row was deleted:
            return cursor.rowcount > 0

    def verify_user(self, username, password):
        """Verify if the username and password pair is correct."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            hashed_password = self._hash_password(password)
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, hashed_password),
            )
            # using fetchone() to verify if the interogation for username and password returned a value:
            return cursor.fetchone() is not None
