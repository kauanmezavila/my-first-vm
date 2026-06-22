import shlex

try:
    import readline  # noqa: F401
except ImportError:
    pass

from src.pkgs.pathresolve import *
BIOS_ROOT = init_root_path(0)

from terminal_pkg import *
from files_bios import FILES
from deploy import deploy

actual_dir: str | None = None

actual_path: list = []


def get_current_dir():
    current = FILES

    for part in actual_path:
      current = current[part]

    return current


def edit_entry(cmd):
    if cmd[0] not in ("mkdir", "rmdir", "touch", "rm"):
        return False

    if len(cmd) < 2:
        print("\n[ERROR] Missing name.")
        return True

    current = get_current_dir()
    name = cmd[1]

    if cmd[0] == "mkdir":
        if name in current:
            print(f"\n[ERROR] File exists: {name}")
        else:
            current[name] = {}

    elif cmd[0] == "touch":
        if isinstance(current.get(name), dict):
            print(f"\n[ERROR] {name} is a directory.")
        else:
            current[name] = current.get(name, "")

    elif name not in current:
        print(f"\n[ERROR] Not found: {name}")

    elif cmd[0] == "rmdir":
        if not isinstance(current[name], dict):
            print(f"\n[ERROR] {name} is not a directory.")
        elif current[name]:
            print(f"\n[ERROR] Directory not empty: {name}")
        else:
            del current[name]

    elif isinstance(current[name], dict):
        print(f"\n[ERROR] {name} is a directory, use rmdir.")

    else:
        del current[name]

    return True



splash: str = main_splash()


if splash == "Start":
    clear()

    bios_banner()
    try:
        while True:
            path = "~" if not actual_path else "(~/" + "/".join(actual_path) + ")"
            cmd = shlex.split(input(f"\nroot@main-vm{path}$: "))

            if cmd == None or len(cmd) == 0:
                pass
                   
            elif cmd[0] == "clear":
                clear()

            elif cmd[0] == "cd":
                if len(cmd) < 2:
                    print("\n[ERROR] Missing directory.")

                elif cmd[1] == "..":
                    if actual_path:
                        actual_path.pop()

                else:
                    current = get_current_dir()

                    if cmd[1] in current and isinstance(current[cmd[1]], dict):
                        actual_path.append(cmd[1])
                    elif cmd[1] in current:
                        print(f"\n[ERROR] {cmd[1]} is a file, only use cd on directories.")
                    else:
                        print(f"\n[ERROR] Directory not found: {cmd[1]}")


            elif cmd[0] == "ls":
                current = get_current_dir()

                if isinstance(current, dict):
                    for name in current.keys():
                        print(f"\n{name}")

            elif cmd[0] == "pwd":
                if not actual_path:
                    print("\nBIOS/")
                else:
                    print("\nBIOS/" + "/".join(actual_path))

            elif cmd[0] == "cat":
                if len(cmd) < 2:
                    print("\n[ERROR] Missing file.")

                else:
                    current = get_current_dir()
                    target = cmd[1]

                    if target not in current:
                        print(f"\n[ERROR] File not found: {target}")

                    elif isinstance(current[target], dict):
                        print(f"\n[ERROR] {target} is a directory, use ls or cd.")

                    else:
                        print(f"\n{current[target]}")

            elif edit_entry(cmd):
                pass

            elif cmd[0] == "exit":
                print("\n[ OK ] Shutting down...")
                break

            elif cmd[0] == "help":
                print("""\nAvailable commands:
  clear           Clear the terminal screen.
  cd <dir>        Change the current directory to <dir>. Use '..' to go up one level.
  ls              List the contents of the current directory.
  pwd             Print the current directory path.
  cat <file>      Display the contents of <file>.
  mkdir <dir>     Create a directory.
  rmdir <dir>     Remove an empty directory.
  touch <file>    Create an empty file.
  rm <file>       Remove a file.
  deploy <.iso>   Deploy and start a .iso
  exit            Exit the terminal.
  help            Show this help message.
                """)

            elif cmd[0] == "deploy":
                if len(cmd) < 2:
                    print("\n[ERROR] The .iso file is missing")

                else:
                    current = get_current_dir()
                    target = cmd[1]

                    if target not in current:
                        print(f"\n[ERROR] File not found: {target}")

                    elif isinstance(current[target], dict):
                        print(f"\n[ERROR] {target} is a directory, use ls or cd.")

                    else:
                        print(f"[ OK ] Deploying and starting {target}")
                        deploy(current[target])

            else:
                print(f"\n[ERROR] Command not found: {cmd[0]}")


    except KeyboardInterrupt:
        print("\n\n[ OK ] Shutting down...")

else:
    clear()
