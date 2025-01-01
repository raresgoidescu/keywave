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
        ret = client.send_acc_create()

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


def main(client: Client):
    while True:
        # clear_screen()
        # print(f'Welcome, {client.username}!')

        while len(client.pending_invites) > 0:
            choice = input(f"You have a pending chat invite from {client.pending_invites[-1]}, accept? [y/n]: ")

            if choice == 'y':
                # todo client.accept_invite()
                # todo take client to chat interface
                break
            else:
                # todo client.reject_invite()
                client.pending_invites.pop()

        CHOICE_MSG = 1
        CHOICE_FRIEND_ADD = 2
        CHOICE_FRIEND_RM = 3
        CHOICE_REFRESH = 4
        CHOICE_EXIT = 0

        print("\nChoose an option:")
        print("1. Start a chat")
        print("2. Add friend")
        print("3. Remove friend")
        print("4. Refresh")
        print("0. Exit")

        choice = input("\nEnter your choice: ")

        if choice.isdigit():
            choice = int(choice)

            if choice == CHOICE_MSG:
                print("\nYour friends:")
                for i, friend in enumerate(client.friends, start = 1):
                    print(f"{i}. {friend}")

                friend_username = input("Enter friend's username (or index from quick select): ")

                if friend_username.isdigit():
                    friend_index = int(friend_username) - 1
                    if friend_index < 0 or friend_index >= len(client.friends):
                        print(f'Invalid input')
                        continue

                    friend_username = client.friends[friend_index]

                print(f"Waiting for {friend_username} to accept chat invite...")
                print(f"This may take up to 30 seconds, press CTRL-C to cancel invite")

                try:
                    chat_started = client.start_chat(friend_username)
                except KeyboardInterrupt:
                    # todo client.cancel_chat_invite()
                    continue

                if not chat_started:
                    print(f"[INFO] Cannot start chat with user '{friend_username}'")
                    continue

                first_render = True
                while True:
                    clear_screen()
                    if first_render:
                        print(f'New chat started with {friend_username}')
                    else:
                        print(f'Chat with {friend_username}')
                        client.get_updates()

                        for message in client.logs[friend_username]:
                            print(message)

                    first_render = False
                    print("(Type your message, '/r' to refresh or '/b' to go back.)")

                    message = input("> ").strip()

                    if (message == "/b"):
                        break

                    if (message == "/r"):
                        continue
                    
                    if log_level >= 2:
                        print(f"[INFO] Sending \"{message}\" sent to {friend_username}...")
                    res = client.send_message(friend_username, message)
                    if log_level >= 2:
                        print(f"[INFO] Server said '{res}'")
                    client.log_new_message(friend_username, message, own_message=True)

            elif choice == CHOICE_FRIEND_ADD:
                text = input("Enter the name of the new friend (/b to go back): ").strip()

                if (text == "/b"):
                    continue

                if text:
                    if text not in client.friends:
                        client.friends.append(text)
                        print(f"{text} has been added to your friends list.")
                    else:
                        print(f"{text} is already in your friends list.")
                else:
                    print("Friend name cannot be empty.")

            elif choice == CHOICE_FRIEND_RM:
                # Remove friend
                print("\nYour friends:")
                for i, friend in enumerate(client.friends, start = 1):
                    print(f"{i}. {friend}")

                friend_index = input("(/b to go back) Choose a friend to remove (by number): ")

                if (friend_index == "/b"):
                    continue

                if friend_index.isdigit():
                    friend_index = int(friend_index) - 1
                    if 0 <= friend_index < len(client.friends):
                        confirmation = input("Are you sure? [y/n] ")

                        if confirmation == "n":
                            continue

                        removed_friend = client.friends.pop(friend_index)

                        print(f"{removed_friend} has been removed from your friends list.")
                    else:
                        print("Invalid choice. Please select a valid friend.")
                    continue
                else:
                    print("Invalid input. Please enter a valid number.")

            elif choice == CHOICE_REFRESH:
                client.get_updates()
                continue

            elif choice == CHOICE_EXIT:
                client.disconnect()
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
    client.set_log_level(log_level)
    client.connect(("0.0.0.0", PORT))

    while (client.logged_in == False):
        choice = get_account_action()
        process_account_action(choice, client)

    clear_screen()

    main(client)

