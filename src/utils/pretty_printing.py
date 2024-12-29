# ANSI escape sequences for text formatting
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

# Color codes
COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "default": "\033[39m",
}

def format_message(message: str, color = "default", bold = False, underline = False):
    """
    Format a message with color, bold, and underline styles.

    Args:
        message (str): The message to format.
        color (str): The color of the text (default: "default").
        bold (bool): Whether to make the text bold (default: False).
        underline (bool): Whether to underline the text (default: False).

    Returns:
        str: The formatted message.
    """
    style = COLORS.get(color.lower(), COLORS["default"])
    if bold:
        style += BOLD
    if underline:
        style += UNDERLINE

    return f"{style}{message}{RESET}"
