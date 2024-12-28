#!/usr/bin/env python3

from database import Database

def main():
    db = Database()

    while True:
        print("\nChoose an option:")
        print("1. Add User")
        print("2. Delete User")
        print("3. Verify User")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            if db.add_user(username, password):
                print("User added successfully.")
            else:
                print("Error: User already exists.")

        elif choice == "2":
            username = input("Enter username to delete: ")
            password = input("Enter password: ")

            ret = db.delete_user(username, password)
            if ret:
                print("User deleted successfully.")
            else:
                print("Invalid username or password")

        elif choice == "3":
            username = input("Enter username: ")
            password = input("Enter password: ")
            if db.verify_user(username, password):
                print("Login successful.")
            else:
                print("Invalid username or password.")
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
