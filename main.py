#! /usr/bin/env python3

import getpass
import os

from src.client.client import Client
from src.utils.pretty_formatting import prettyf

global log_level
log_level = 0

def clear_screen():
    if "x" in os.name:
        _ = os.system('clear')
    else:
        _ = os.system('cls')


def set_log_level():
    prompt = prettyf("Choose LOG_LEVEL: No logs (0), Errors (1), All (2): ", bold = True, color = "green")
    choice = input(prompt)
    stripped_choice = choice.lstrip("-")

    if not choice.isnumeric() or choice != stripped_choice:
        print(prettyf("Invalid choice (not numeric)", bold = True, color = "red"))
        return False

    choice = int(choice)

    if choice > 2:
        print(prettyf("Invalid choice", bold = True, color = "red"))
        return False

    global log_level
    log_level = choice

    return True


def get_account_action():
    prompt = prettyf("Login (1), Create Account (2): ", bold = True)
    choice = input(prompt)
    stripped_choice = choice.lstrip("-")

    if not choice.isnumeric() or choice != stripped_choice:
        print(prettyf("Invalid choice (not numeric)", bold = True, color = "red"))
        return 404;

    return int(choice)


def process_account_action(choice: int, client: Client) -> bool:
    if choice == 1: # Login
        username = input("Username: ")
        password = getpass.getpass("Password: ")

        client.set_credentials(username, password)
        ret = client.send_acc_login()

        return client.logged_in

    if choice == 2: # Create account
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Confirm Password: ")

        if password != password_confirm:
            print(prettyf("Passwords don't match!"))
            return False

        client.set_credentials(username, password)
        ret = client.send_acc_create()

        return client.logged_in

    print(prettyf("Invalid option", bold = True, color = "red"))

    return False


def main(client: Client):
    while True:
        clear_screen()

        accepted_invite = None
        while len(client.pending_invites) > 0:
            pending_inv_username = client.pending_invites[-1]['source']
            known = client.pending_invites[-1]['known']

            known_msg = ' (you\'ve never talked to them before)' if not known else ''
            choice = input(f"You have a pending chat invite from {pending_inv_username}{known_msg}, accept? [y/n]: ")

            if choice == 'y':
                inv_acc_response = client.accept_invite()
                if inv_acc_response == 'success':
                    accepted_invite = pending_inv_username
                    break

                print(f'[ERROR] Failed to accept invite, server response: "{inv_acc_response}"')
                client.pending_invites.pop()
            else:
                client.reject_invite()

        CHOICE_MSG = 1
        CHOICE_REFRESH = 2
        CHOICE_EXIT = 0

        main_choice = -1
        if accepted_invite is not None:
            main_choice = '1'
        else:
            print("\nChoose an option:")
            print("1. Start a chat")
            print("2. Refresh")
            print("0. Exit")

            main_choice = input("\nEnter your choice: ")

        if main_choice.isdigit():
            main_choice = int(main_choice)

            if main_choice == CHOICE_MSG:
                key = None

                friend_username = ""
                if accepted_invite is not None:
                    friend_username = accepted_invite

                    # for the client who accepts the chat
                    if log_level >= 2:
                        print(f'[INFO] Client B waiting for key exchange...')

                    key = client.begin_key_exchange(friend_username, role=2)

                    client.set_key(key)

                    if log_level >= 2:
                        print(f"[INFO] Key is set to {key}")

                else:
                    print("\nYour prior connections:")
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

                    # for the client who starts the chat
                    if log_level >= 2:
                        print("[INFO] Client A waiting on key exchange...")
                    key = client.begin_key_exchange(friend_username, role=1)

                    client.set_key(key)
                    if log_level >= 2:
                        print(f"[INFO] Key is set to {key}")

                first_render = True
                while True:
                    clear_screen()
                    if first_render:
                        print(f'New chat started with {friend_username}')
                        client.add_connection(friend_username)
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

            elif main_choice == CHOICE_REFRESH:
                client.get_updates()
                continue

            elif main_choice == CHOICE_EXIT:
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

