#!/usr/bin/env python3

import src.utils.pretty_printing as prettyf
import getpass
import os

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


def process_account_action(choice: int):
    if choice == 1: # Login
        username = input("> Username: ")
        password = getpass.getpass("> Password: ")

        ret = 1 # TODO: send login req

        if (ret == 1):
            return True
        else:
            return False

    if choice == 2: # Create account
        username = input("> Username: ")
        password = getpass.getpass("> Password: ")
        password_confirm = getpass.getpass("> Confirm Password: ")

        if password != password_confirm:
            err = prettyf.format_message("Passwords don't match!")
            print(err)
            return False

        # TODO: send_create_req

        return True

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


if __name__ == "__main__":
    clear_screen()

    log_level_set = False

    while (log_level_set == False):
        log_level_set = set_log_level()

    logged = False

    clear_screen()

    while (logged == False):
        choice = get_account_action()
        logged = process_account_action(choice)

    clear_screen()
