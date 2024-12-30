#! /usr/bin/env python3
            
import src.utils.pretty_printing as prettyf
import getpass
import os

from src.client.client import Client


global log_level
log_level = 0

def clear_screen():
    if "x" in os.name:
        _ = os.system('clear')
    else:
        _ = os.system('cls')


def set_log_level():
    prompt = prettyf.format_message(
            ">> Choose LOG_LEVEL: No logs (0), Errors (1), All (2): ",
            bold = True, color = "green"
            )
    choice = input(prompt)
    stripped_choice = choice.lstrip("-")

    if not choice.isnumeric() or choice != stripped_choice:
        print(prettyf.format_message("Invalid choice (not numeric)", bold = True, color = "red"))
        return False

    choice = int(choice)

    if choice > 2:
        print(prettyf.format_message("Invalid choice", bold = True, color = "red"))
        return False

    global log_level
    log_level = choice

    return True


def get_account_action():
    prompt = prettyf.format_message(">> Login (1), Create Account (2), Delete Account (0): ", bold=True)
    choice = input(prompt)
    stripped_choice = choice.lstrip("-")

    if not choice.isnumeric() or choice != stripped_choice:
        print(prettyf.format_message("Invalid choice (not numeric)", bold = True, color = "red"))
        return 404;

    return int(choice)


def process_account_action(choice: int, client: Client) -> bool:
    if choice == 1: # Login
        username = input("> Username: ")
        password = getpass.getpass("> Password: ")

        client.set_credentials(username, password)
        ret = client.send_acc_login()

        return client.logged_in

    if choice == 2: # Create account
        username = input("> Username: ")
        password = getpass.getpass("> Password: ")
        password_confirm = getpass.getpass("> Confirm Password: ")

        if password != password_confirm:
            err = prettyf.format_message("Passwords don't match!")
            print(err)
            return False

        client.set_credentials(username, password)
        ret = client.send_acc_create(username, password)

        return client.logged_in

    if choice == 0: # Delete
        username = input("> Username: ")
        password = getpass.getpass("> Password: ")
        password_confirm = getpass.getpass("> Confirm Password: ")

        if password != password_confirm:
            err = prettyf.format_message("Passwords don't match!")
            print(err)
            return False

        confirmation = input(
                prettyf.format_message("Are you sure? [y/n] ", bold = True, color = "red")
                )

        if confirmation == "y":
            # TODO: send_delete_req
            _ = "TODO"

        return False

    print(prettyf.format_message("Invalid option", bold = True, color = "red"))

    return False


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

PORT = 18251
if __name__ == "__main__":   
    clear_screen()

    log_level_set = False

    while (log_level_set == False):
        log_level_set = set_log_level()

    clear_screen()

    client = Client()
    client.connect(("0.0.0.0", PORT))

    while (client.logged_in == False):
        choice = get_account_action()
        process_account_action(choice, client)

    clear_screen()

    print(f'Welcome, {client.username}!')

    main()

