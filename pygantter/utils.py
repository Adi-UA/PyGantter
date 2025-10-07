from typing import Any, Iterable

from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)


def progress_bar(
    iterable: Iterable[Any], desc: str = "Processing", color: str = Fore.CYAN
) -> Iterable[Any]:
    return tqdm(iterable, desc=f"{color}{desc}{Style.RESET_ALL}")


def format_error(msg: str) -> str:
    return f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}"


def format_warning(msg: str) -> str:
    return f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {msg}"
