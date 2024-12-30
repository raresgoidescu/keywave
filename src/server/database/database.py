import sqlite3
import hashlib

class Database:
    def __init__(self, db_name="./users.db"):
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
            # always should be: user1_id < user2_id
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS connections (
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    FOREIGN KEY (user1_id) REFERENCES users (id),
                    FOREIGN KEY (user2_id) REFERENCES users (id),
                    UNIQUE(user1_id, user2_id)
                )
                """
            )
            # using commit() to save the changes:
            conn.commit()

    def _hash_password(self, password):
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    
    def add_user(self, username, password):
        '''
        attempt to add a new user 

        return user id on succes, or -1 on failure 
        '''
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                hashed_password = self._hash_password(password)
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password),
                )
                conn.commit()

                new_id = cursor.lastrowid

                print(f'[INFO] Database: created acc with id = {new_id}')
                return new_id
        except sqlite3.IntegrityError:
            return -1

    def delete_user(self, username, password):
        """
        Delete a user from the database if the password is correct.
        """
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

            user = cursor.fetchone()
            if user is None:
                return -1
            
            return user[0]
        

    def get_uid(self, username):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

            user = cursor.fetchone()
            if user is None:
                return False
            
            return user[0]

    def __verify_user_by_id(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

            user = cursor.fetchone()
            if user is None:
                return False
            
            return True

    def add_connection(self, user1_id, user2_id):
        """Add a connection between two users."""
        if not self.__verify_user_by_id(user1_id) or not self.__verify_user_by_id(user2_id):
            print(f'[INFO] Database: user1_id = {user1_id} or user2_id = {user2_id} does not exist')
            return False

        user1_id, user2_id = sorted((user1_id, user2_id))
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO connections (user1_id, user2_id) VALUES (?, ?)",
                (user1_id, user2_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def remove_connection(self, user1_id, user2_id):
        """Remove a connection between two users."""
        if not self.__verify_user_by_id(user1_id) or not self.__verify_user_by_id(user2_id):
            print(f'[INFO] Database: user1_id = {user1_id} or user2_id = {user2_id} does not exist')
            return False

        user1_id, user2_id = sorted((user1_id, user2_id))
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM connections WHERE user1_id = ? AND user2_id = ?",
                (user1_id, user2_id),
            )
            conn.commit()
            return cursor.rowcount > 0
