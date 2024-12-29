#! /usr/bin/env python3

def main():
    friends = ["cristi", "dani", "rares", "mihai"]

    while True:
        print("\nChoose an option:")
        print("1. Send message")
        print("2. Add friend")
        print("3. Remove friend")
        print("4. Exit")

        choice = input("\nEnter your choice: ")

        if choice.isdigit():
            choice = int(choice)

            if choice == 1:
                print("\nYour friends:")
                for i, friend in enumerate(friends, start = 1):
                    print(f"{i}. {friend}")

                friend_index = input("Choose a friend to message (by number): ")

                if friend_index.isdigit():
                    friend_index = int(friend_index) - 1

                    if (0 <= friend_index) and (friend_index < len(friends)):
                        print("(Type '/back' to go back.)")
                        while True:
                            message = input("Enter your message> ").strip()

                            if (message == "/back"):
                                break

                            print(f"Message \"{message}\" sent to {friends[friend_index]}!")
                    else:
                        print("Invalid choice. Please select a valid friend.")
                else:
                    print("Invalid input. Please enter a valid number.")

            elif choice == 2:
                text = input("Enter the name of the new friend (or /back): ").strip()

                if (text == "/back"):
                    continue

                if text:
                    if text not in friends:
                        friends.append(text)
                        print(f"{text} has been added to your friends list.")
                    else:
                        print(f"{text} is already in your friends list.")
                else:
                    print("Friend name cannot be empty.")

            elif choice == 3:
                # Remove friend
                print("\nYour friends:")
                for i, friend in enumerate(friends, start=1):
                    print(f"{i}. {friend}")

                friend_index = input("(/back to go back) Choose a friend to remove (by number): ")

                if (friend_index == "/back"):
                    continue

                if friend_index.isdigit():
                    friend_index = int(friend_index) - 1
                    if 0 <= friend_index < len(friends):
                        confirmation = input("Are you sure? [y/n] ")

                        if confirmation == "n":
                            continue

                        removed_friend = friends.pop(friend_index)

                        # TODO: client.remove_friend(username)

                        print(f"{removed_friend} has been removed from your friends list.")
                    else:
                        print("Invalid choice. Please select a valid friend.")
                    continue
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

