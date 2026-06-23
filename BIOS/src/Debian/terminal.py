import shlex
import os
import importlib
import importlib.util
from typing import Any, Callable

try:
    import readline
except ImportError:
    pass

from pathresolve import init_root_path
BIOS_ROOT = init_root_path(2)

from src.pkgs.colorme import *
from src.pkgs.neofetch import *
from src.Debian.terminal_pkg import *
from src.Debian.files_vm import FILES

from VMs.Debian.init_pkg import MANIFEST

COMMANDS: dict[str, Callable[..., object]] = {
    "clear": clear,
    "whoami": whoami,
    "uname": uname,
    "hostname": hostname,
    "date": date,
}

DOWNLOADED_PKGS = ["colorme", "pathresolve"]

actual_path: list[str] = []


def get_current_dir() -> dict[str, Any]:
    current: dict[str, Any] = FILES

    for part in actual_path:
        next_dir = current[part]
        if not isinstance(next_dir, dict):
            return {}
        current = next_dir

    return current


def edit_entry(cmd: list[str]) -> bool:
    if cmd[0] not in ("mkdir", "rmdir", "touch", "rm"):
        return False

    if len(cmd) < 2:
        print(f"\n[{RED}ERROR{WHITE}] Missing name.")
        return True

    current = get_current_dir()
    name = cmd[1]

    if cmd[0] == "mkdir":
        if name in current:
            print(f"\n[{RED}ERROR{WHITE}] File exists: {name}")
        else:
            current[name] = {}

    elif cmd[0] == "touch":
        if isinstance(current.get(name), dict):
            print(f"\n[{RED}ERROR{WHITE}] {name} is a directory.")
        elif name in current:
            print(f"\n[{RED}ERROR{WHITE}] File exists: {name}")
        else:
            current[name] = current.get(name, "")

    elif name not in current:
        print(f"\n[{RED}ERROR{WHITE}] Not found: {name}")

    elif cmd[0] == "rmdir":
        if not isinstance(current[name], dict):
            print(f"\n[{RED}ERROR{WHITE}] {name} is not a directory.")
        elif current[name]:
            print(f"\n[{RED}ERROR{WHITE}] Directory not empty: {name}")
        else:
            del current[name]

    elif isinstance(current[name], dict):
        print(f"\n[{RED}ERROR{WHITE}] {name} is a directory, use rmdir.")

    else:
        del current[name]

    return True


USER = FILES["etc"]["username"]
HOST = FILES["etc"]["hostname"]

try:
    load_pkgs = question("Want to load pkgs on DEFAULT", "y")
    if load_pkgs == True:
        for pkg in load_persistency("src/Debian/DEFAULT.json").get(".installed_pkgs", []):
            module = importlib.import_module(f"src.pkgs.{pkg}")
            module.main_call(COMMANDS, MANIFEST, get_current_dir)
            DOWNLOADED_PKGS.append(pkg)

    while True:
        
        path = "~" if not actual_path else "(~/" + "/".join(actual_path) + ")"
        cmd = shlex.split(input(f"\n{RED}{USER}{WHITE}@{RED}{HOST}{GREEN}{path}{WHITE}$: "))

        if len(cmd) == 0:
            continue


        elif cmd[0] == "cd":
            if len(cmd) < 2:
                print(f"\n[{RED}ERROR{WHITE}] Missing directory.")

            elif cmd[1] == "..":
                if actual_path:
                    actual_path.pop()

            else:
                current = get_current_dir()

                if cmd[1] in current and isinstance(current[cmd[1]], dict):
                    actual_path.append(cmd[1])
                elif cmd[1] in current:
                    print(f"\n[{RED}ERROR{WHITE}] {cmd[1]} is a file, only use cd on directories.")
                else:
                    print(f"\n[{RED}ERROR{WHITE}] Directory not found: {cmd[1]}")


        elif cmd[0] == "ls":
            current = get_current_dir()

            if isinstance(current, dict):
                for name in current.keys():
                    print(f"\n{name}")

        elif cmd[0] == "pwd":
            print("\n/" + "/".join(actual_path) if actual_path else "/")

        elif cmd[0] == "cat":
            if len(cmd) < 2:
                print(f"\n[{RED}ERROR{WHITE}] Missing file.")

            else:
                current = get_current_dir()
                target = cmd[1]

                if target not in current:
                    print(f"\n[{RED}ERROR{WHITE}] File not found: {target}")

                elif isinstance(current[target], dict):
                    print(f"\n[{RED}ERROR{WHITE}] {target} is a directory, use ls or cd.")

                else:
                    print(f"\n{current[target]}")

        elif edit_entry(cmd):
            pass

        elif cmd[0] == "passwd":
            change_uname = question(f"Want to change {USER} to {cmd[1]}", "n")
            if change_uname == True:
                FILES["etc"]["username"] = cmd[1]
                USER = FILES["etc"]["username"]
                print(f"\n[ {GREEN}OK{WHITE} ] Username changed! Hi {USER}!")
            else:
                print(f"\n[{RED}ERROR{WHITE}] Action cancelled by user")

        elif cmd[0] == "exit":

            quest = question("Want to save your changes on files", "n")

            if quest == True:
                save = save_persistency(FILES)
                print(f"\n[ {GREEN}OK{WHITE} ] Saved!")

            else:
                pass

            print(f"\n[ {GREEN}OK{WHITE} ] Shutting down...")
            break

        elif cmd[0] == "help":
            print("""
Built-in commands:

  clear           Clear the terminal screen.
  cd <dir>        Change the current directory to <dir>. Use '..' to go up one level.
  ls              List the contents of the current directory.
  pwd             Print the current directory path.
  cat <file>      Display the contents of <file>.
  mkdir <dir>     Create a directory.
  rmdir <dir>     Remove an empty directory.
  touch <file>    Create an empty file.
  rm <file>       Remove a file.
  exit            Exit the terminal.
  help            Show this help message.                                   
""")

        elif cmd[0] == "echo":
            echo(" ".join(cmd[1:]))

        elif cmd[0] == "loadp":
            try:
                saved_files = load_persistency("src/Debian/FILES.json")
                FILES.clear()
                FILES.update(saved_files)
            except FileNotFoundError:
                print(f"\n[{RED}ERROR{WHITE}] No saved files.")

        elif cmd[0] == "restp":
            try:
                default_files = load_persistency("src/Debian/DEFAULT.json")
                FILES.clear()
                FILES.update(default_files)
            except FileNotFoundError:
                print(f"\n[{RED}ERROR{WHITE}] No default files.")

        elif cmd[0] == "apt":
            if len(cmd) < 2:
                print(f"\n[{RED}ERROR{WHITE}] Missing args, try install or list")
                continue

            if cmd[1] == "install":
                if len(cmd) < 3:
                    print(f"\n[{RED}ERROR{WHITE}] Missing package name.")
                    continue

                pkg = cmd[2]

                if pkg not in DOWNLOADED_PKGS:
                    if pkg.isidentifier() and importlib.util.find_spec(f"src.pkgs.{pkg}"):
                        module = importlib.import_module(f"src.pkgs.{pkg}")
                        module.main_call(COMMANDS, MANIFEST, get_current_dir)


                        save_pkgs = question("Want to save on DEFAULT", "y")
                        if save_pkgs == True:
                            default_files = load_persistency("src/Debian/DEFAULT.json")
                            default_files.setdefault(".installed_pkgs", [])
                            if pkg not in default_files[".installed_pkgs"]:
                                default_files[".installed_pkgs"].append(pkg)
                            save_persistency(default_files, "src/Debian/DEFAULT.json")
                        DOWNLOADED_PKGS.append(pkg)
                
                    else:
                        print(f"\n[{RED}ERROR{WHITE}] The pkg {pkg} don't exist")
                
                else:
                    if pkg in COMMANDS:
                       print(f"\n[{RED}ERROR{WHITE}] '{pkg}' is already in sy stem, try to run {pkg}")
                    else:
                        print(f"\n[{RED}ERROR{WHITE}] '{pkg}' is already in system")

            elif cmd[1] == "list":
                pkgs_list: list = []

                with os.scandir(BIOS_ROOT / r"src/pkgs/") as files:
                    for file in files:
                        if file.is_file():
                            pkgs_list.append(file.name.replace(".py", ""))
                print("\nAvaliable pkgs on src:")
                for pkg in pkgs_list:
                    print(f"    {pkg} {"(ON)" if pkg in DOWNLOADED_PKGS else ""}")

            else:
                print(f"\n[{RED}ERROR{WHITE}] Use: apt install <pkg>")

        elif cmd[0] in COMMANDS:
            func = COMMANDS[cmd[0]]

            try:
                func(cmd)
            except TypeError:
                func()

        else:
            print(f"\n[{RED}ERROR{WHITE}] Command not found: {cmd[0]}")


except KeyboardInterrupt:
    print(f"\n\n[ {GREEN}OK{WHITE} ] Shutting down...")
