import shlex
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

actual_path: list[str] = []


def get_current_dir() -> dict[str, Any]:
    current: dict[str, Any] = FILES

    for part in actual_path:
        next_dir = current.get(part)
        if not isinstance(next_dir, dict):
            actual_path.clear()
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

MANIFEST["user"] = USER
MANIFEST["host"] = HOST

try:
    load_pkgs = question("Want to load pkgs on DEFAULT", "y")
    if load_pkgs == True:
        try:
            pkgs = load_persistency("src/Debian/DEFAULT.json").get(".installed_pkgs", [])
        except (OSError, ValueError) as exc:
            print_error(f"Could not load DEFAULT pkgs: {exc}")
            pkgs = []
        for pkg in pkgs:
            if valid_pkg_name(pkg):
                load_package(pkg, COMMANDS, MANIFEST, get_current_dir)
            else:
                print_error(f"Invalid pkg name on DEFAULT: {pkg}")

    while True:
        
        path = "~" if not actual_path else "(~/" + "/".join(actual_path) + ")"
        try:
            cmd = shlex.split(input(f"\n{RED}{USER}{WHITE}@{RED}{HOST}{GREEN}{path}{WHITE}$: "))
        except ValueError as exc:
            print_error(str(exc))
            continue
        except EOFError:
            print(f"\n[ {GREEN}OK{WHITE} ] Shutting down...")
            break

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
            if len(cmd) < 2:
                print_error("Missing username.")
                continue

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
                try:
                    save_persistency(FILES)
                    print(f"\n[ {GREEN}OK{WHITE} ] Saved!")
                except OSError as exc:
                    print_error(f"Could not save files: {exc}")

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
  apt update      Update local package files from the remote repo.
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
                print_error("No saved files.")
            except OSError as exc:
                print_error(f"Could not load saved files: {exc}")
            except ValueError as exc:
                print_error(f"Saved files are invalid: {exc}")

        elif cmd[0] == "restp":
            try:
                default_files = load_persistency("src/Debian/DEFAULT.json")
                FILES.clear()
                FILES.update(default_files)
            except FileNotFoundError:
                print_error("No default files.")
            except OSError as exc:
                print_error(f"Could not load default files: {exc}")
            except ValueError as exc:
                print_error(f"Default files are invalid: {exc}")

        elif cmd[0] == "apt":
            handle_apt(cmd, COMMANDS, MANIFEST, get_current_dir)

        elif cmd[0] in COMMANDS:
            func = COMMANDS[cmd[0]]

            try:
                func(cmd)
            except TypeError:
                try:
                    func()
                except TypeError as exc:
                    print_error(f"Bad usage for '{cmd[0]}': {exc}")
                except Exception as exc:
                    print_error(f"Command '{cmd[0]}' failed: {exc}")
            except Exception as exc:
                print_error(f"Command '{cmd[0]}' failed: {exc}")

        else:
            print(f"\n[{RED}ERROR{WHITE}] Command not found: {cmd[0]}")


except KeyboardInterrupt:
    print(f"\n\n[ {GREEN}OK{WHITE} ] Shutting down...")
