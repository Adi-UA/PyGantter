"""Small terminal-formatting helpers for CLI messages."""

from __future__ import annotations

from colorama import Fore, Style, init

init(autoreset=True)


def format_error(message: str) -> str:
    """Return ``message`` tagged as an error, colored red."""
    return f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}"


def format_warning(message: str) -> str:
    """Return ``message`` tagged as a warning, colored yellow."""
    return f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}"


def format_success(message: str) -> str:
    """Return ``message`` tagged as success, colored green."""
    return f"{Fore.GREEN}[OK]{Style.RESET_ALL} {message}"
