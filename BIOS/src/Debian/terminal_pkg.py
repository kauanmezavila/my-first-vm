import os
import time
import json
import sys
import tempfile
import importlib
import importlib.util
import requests
from requests import RequestException
from tqdm import tqdm
from typing import Callable

from pathresolve import init_root_path
BIOS_ROOT = init_root_path(2)

init_root_path(2)

from src.Debian.files_vm import FILES
from src.pkgs.colorme import *

REMOTE_PKG_URL = "https://raw.githubusercontent.com/kauanmezavila/my-first-vm-repo/refs/heads/main/{pkg}.py"
DOWNLOADED_PKGS = ["colorme", "pathresolve"]
PKG_COMMANDS: dict[str, list[str]] = {}


def print_error(message: str) -> None:
    print(f"\n[{RED}ERROR{WHITE}] {message}")


def valid_pkg_name(pkg: str) -> bool:
    return pkg.isidentifier() and not pkg.startswith("_")


def load_package(
    pkg: str,
    commands: dict[str, Callable[..., object]],
    manifest: dict,
    get_current_dir: Callable,
) -> bool:
    try:
        module = importlib.import_module(f"src.pkgs.{pkg}")
        before = set(commands)
        module.main_call(commands, manifest, get_current_dir)
    except (ImportError, AttributeError, TypeError) as exc:
        print_error(f"Could not load pkg '{pkg}': {exc}")
        return False

    PKG_COMMANDS[pkg] = list(set(commands) - before)
    if pkg not in DOWNLOADED_PKGS:
        DOWNLOADED_PKGS.append(pkg)
    return True


def save_installed_pkg(pkg: str) -> None:
    try:
        default_files = load_persistency("src/Debian/DEFAULT.json")
        default_files.setdefault(".installed_pkgs", [])
        if pkg not in default_files[".installed_pkgs"]:
            default_files[".installed_pkgs"].append(pkg)
        save_persistency(default_files, "src/Debian/DEFAULT.json")
    except (OSError, ValueError) as exc:
        print_error(f"Could not save pkg '{pkg}' on DEFAULT: {exc}")


def remove_installed_pkg(pkg: str) -> None:
    try:
        default_files = load_persistency("src/Debian/DEFAULT.json")
        if pkg in default_files.get(".installed_pkgs", []):
            default_files[".installed_pkgs"].remove(pkg)
            save_persistency(default_files, "src/Debian/DEFAULT.json")
    except (OSError, ValueError) as exc:
        print_error(f"Could not update DEFAULT: {exc}")


def download_package(pkg: str) -> bool:
    url = REMOTE_PKG_URL.format(pkg=pkg)
    target = BIOS_ROOT / "src" / "pkgs" / f"{pkg}.py"

    try:
        print(f"{BLUE}[*]{RESET} Connecting with {url}...")
        with requests.get(url, stream=True, timeout=15) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            print(f"{BLUE}Get:{RESET} {pkg}.py [{total/1024:.1f} kB]")

            with open(target, "wb") as f:
                if total > 100_000:
                    with tqdm(total=total, unit="B", unit_scale=True) as pbar:
                        for chunk in r.iter_content(1024):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    print(f"Downloading {pkg}... ", end="", flush=True)
                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)
                    print(f"{GREEN}Done{RESET}")
    except RequestException as exc:
        print_error(f"Download failed for '{pkg}': {exc}")
        return False
    except OSError as exc:
        print_error(f"Could not write pkg '{pkg}': {exc}")
        return False

    importlib.invalidate_caches()
    print(f"\n[ {GREEN}OK{WHITE} ] {pkg} downloaded!")
    return True


def list_local_pkgs() -> list[str]:
    pkgs: list[str] = []
    with os.scandir(BIOS_ROOT / "src" / "pkgs") as files:
        for file in files:
            if file.is_file() and file.name.endswith(".py"):
                pkgs.append(file.name.removesuffix(".py"))
    return pkgs


def update_packages() -> None:
    updated = 0
    checked = 0

    try:
        pkgs = list_local_pkgs()
    except OSError as exc:
        print_error(f"Could not list pkgs: {exc}")
        return

    for pkg in pkgs:
        if not valid_pkg_name(pkg):
            continue

        checked += 1
        url = REMOTE_PKG_URL.format(pkg=pkg)
        target = BIOS_ROOT / "src" / "pkgs" / f"{pkg}.py"

        try:
            with requests.get(url, timeout=15) as r:
                r.raise_for_status()
                remote_bytes = r.content

            if target.exists() and target.read_bytes() == remote_bytes:
                continue

            with tempfile.NamedTemporaryFile(delete=False, dir="/tmp") as tmp:
                tmp.write(remote_bytes)
                tmp_path = tmp.name
            os.replace(tmp_path, target)
            updated += 1
            print(f"{BLUE}Updated:{RESET} {pkg}.py")
        except RequestException as exc:
            print_error(f"Could not update '{pkg}': {exc}")
        except OSError as exc:
            print_error(f"Could not write '{pkg}': {exc}")

    importlib.invalidate_caches()
    print(f"\n[ {GREEN}OK{WHITE} ] {checked} checked, {updated} updated.")


def handle_apt(
    cmd: list[str],
    commands: dict[str, Callable[..., object]],
    manifest: dict,
    get_current_dir: Callable,
) -> None:
    if len(cmd) < 2:
        print_error("Missing args, try install, update or list")
        return

    if cmd[1] == "update":
        update_packages()
        return

    if cmd[1] == "install":
        if len(cmd) < 3:
            print_error("Missing package name.")
            return

        pkg = cmd[2]
        if pkg in DOWNLOADED_PKGS:
            if pkg in commands:
                print_error(f"'{pkg}' is already in system, try to run {pkg}")
            else:
                print_error(f"'{pkg}' is already in system")
            return

        if not valid_pkg_name(pkg):
            print_error(f"Invalid pkg name: {pkg}")
            return

        if not importlib.util.find_spec(f"src.pkgs.{pkg}") and not download_package(pkg):
            return

        if not load_package(pkg, commands, manifest, get_current_dir):
            return

        if question("Want to save on DEFAULT", "y") == True:
            save_installed_pkg(pkg)
        return

    if cmd[1] == "rm":
        if len(cmd) < 3:
            print_error("Missing package name.")
            return

        pkg = cmd[-1]
        remove_from_src = len(cmd) > 3 and cmd[2] == "-r"

        if not valid_pkg_name(pkg):
            print_error(f"Invalid pkg name: {pkg}")
            return

        if pkg not in DOWNLOADED_PKGS:
            print_error(f"'{pkg}' is not installed")
            return

        if remove_from_src and question(f"Want to delete {pkg} from src repo?", "n"):
            try:
                os.remove(BIOS_ROOT / "src" / "pkgs" / f"{pkg}.py")
            except FileNotFoundError:
                pass
            except OSError as exc:
                print_error(f"Could not delete pkg file: {exc}")
                return

        for name in PKG_COMMANDS.pop(pkg, []):
            commands.pop(name, None)

        while pkg in DOWNLOADED_PKGS:
            DOWNLOADED_PKGS.remove(pkg)
        sys.modules.pop(f"src.pkgs.{pkg}", None)
        remove_installed_pkg(pkg)
        print(f"\n[ {GREEN}OK{WHITE} ] {pkg} removed!")
        return

    if cmd[1] == "list":
        try:
            pkgs = list_local_pkgs()
        except OSError as exc:
            print_error(f"Could not list pkgs: {exc}")
            return

        print("\nAvaliable pkgs on src:")
        for pkg in pkgs:
            status = "(ON)" if pkg in DOWNLOADED_PKGS else ""
            print(f"    {pkg} {status}")
        return

    print_error("Use: apt install <pkg> | apt rm [-r] <pkg> | apt update | apt list")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def question(question_text: str, enphase: str):
    if enphase == "y":
        try:
            quest = input(f"[!] {question_text}? [Y/n]:").strip().lower()
        except EOFError:
            return True
        if quest == "" or quest == None or quest == "y":
            return True
        else:
            return False
        
    elif enphase == "n":
        try:
            quest = input(f"[!] {question_text}? [y/N]:").strip().lower()
        except EOFError:
            return False
        if quest == "" or quest == None or quest == "n":
            return False
        else:
            return True

    else:
        try:
            quest = input(f"[!] {question_text}? [y/n]:").strip().lower()
        except EOFError:
            return False
        if quest == "" or quest == None or quest == "y":
            return True
        else:
            return False
        

def save_persistency(dados, path="src/Debian/FILES.json"):
    with open(BIOS_ROOT / path, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

def load_persistency(path="src/Debian/FILES.json"):
    with open(BIOS_ROOT / path, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def whoami():
    print(FILES["etc"]["username"])

def uname():
    print(FILES["etc"]["uname"])

def hostname():
    print(FILES["etc"]["hostname"])

def date():
    time_now = time.localtime()
    print(f"{time_now.tm_mday}-{time_now.tm_mon}-{time_now.tm_year} {time_now.tm_hour}:{time_now.tm_min}:{time_now.tm_sec}")

def echo(string):
    print(str(string))
