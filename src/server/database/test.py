#!/usr/bin/env python3

from database import Database

def main():
    db = Database()

    while True:
        print("\nConnection Menu:")
        print("1. Add connection")
        print("2. Remove connection")
        print("3. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            user_id1 = input("Enter the first user ID: ").strip()
            user_id2 = input("Enter the second user ID: ").strip()

            if user_id1.isdigit() and user_id2.isdigit():
                user_id1 = int(user_id1)
                user_id2 = int(user_id2)

                if db.add_connection(user_id1, user_id2):
                    print(f"Connection between {user_id1} and {user_id2} added successfully.")

            else:
                print("Invalid input. Please enter valid numeric user IDs.")

        elif choice == "2":
            user_id1 = input("Enter the first user ID: ").strip()
            user_id2 = input("Enter the second user ID: ").strip()

            if user_id1.isdigit() and user_id2.isdigit():
                user_id1 = int(user_id1)
                user_id2 = int(user_id2)

                if db.remove_connection(user_id1, user_id2):
                    print(f"Connection between {user_id1} and {user_id2} removed successfully.")
                else:
                    print(f"No connection exists between {user_id1} and {user_id2}.")
            else:
                print("Invalid input. Please enter valid numeric user IDs.")

        elif choice == "3":
            print("See you later alligator")
            break

        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()

