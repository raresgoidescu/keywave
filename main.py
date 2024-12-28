#! /usr/bin/env python3
import keyboard

def main():
    friends = ["cristi", "dani", "rares", "mihai", "alex", "ion", "gabi", "florin", "vlad", "andrei"]

    while True:
        print("\nChoose an option:")
        print("1. Send message")
        print("2. Add friend")
        print("3. Remove friend")
        print("4. Exit")
        print("Go back: esc")

        choice = input("\nEnter your choice: ")

        if choice.isdigit():
            choice = int(choice)

            if choice == 1:
                while True:
                    print("\nYour friends:")
                    for i, friend in enumerate(friends, start=1):
                        print(f"{i}. {friend}")

                    # print("(Press Esc to go back, Enter to continue) ")
                    # if keyboard.is_pressed("esc"):
                    #     break

                    action = input("(Press Esc to go back, Enter to continue) ")
                    if (action == "esc"):
                        break

                    friend_index = input("Choose a friend to message (by number): ")
                    if friend_index.isdigit():
                        friend_index = int(friend_index) - 1
                        if (0 <= friend_index) and (friend_index < len(friends)):
                            message = input("Enter your message: ").strip()
                            print(f"Message \"{message}\" sent to {friends[friend_index]}!")
                        else:
                            print("Invalid choice. Please select a valid friend.")
                        break
                    else:
                        print("Invalid input. Please enter a valid number.")

            elif choice == 2:
                while True:

                    # print("(Press Esc to go back, Enter to continue) ")
                    # if keyboard.is_pressed("esc"):
                    #     break

                    action = input("(Press Esc to go back, Enter to continue) ")
                    if (action == "esc"):
                        break

                    new_friend = input("Enter the name of the new friend: ").strip()

                    if new_friend:
                        if new_friend not in friends:
                            friends.append(new_friend)
                            print(f"{new_friend} has been added to your friends list.")
                        else:
                            print(f"{new_friend} is already in your friends list.")
                        break
                    else:
                        print("Friend name cannot be empty.")

            elif choice == 3:
                while True:
                    print("\nYour friends:")
                    for i, friend in enumerate(friends, start=1):
                        print(f"{i}. {friend}")

                    # print("(Press Esc to go back, Enter to continue) ")
                    # if keyboard.is_pressed("esc"):
                    #     break

                    action = input("(Press Esc to go back, Enter to continue) ")
                    if (action == "esc"):
                        break

                    friend_index = input("Choose a friend to remove (by number): ")
                    if friend_index.isdigit():
                        friend_index = int(friend_index) - 1
                        if 0 <= friend_index < len(friends):
                            removed_friend = friends.pop(friend_index)
                            print(f"{removed_friend} has been removed from your friends list.")
                        else:
                            print("Invalid choice. Please select a valid friend.")
                        break
                    else:
                        print("Invalid input. Please enter a valid number.")

            elif choice == 4:
                print("See you later alligator")
                break

            else:
                print("Invalid choice. Please select an option between 1 and 4.")
        else:
            print("Invalid input. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
