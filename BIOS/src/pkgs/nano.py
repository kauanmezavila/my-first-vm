def main_call(COMMANDS, MANIFEST=None, get_current_dir=None):
      if get_current_dir is None:
          raise TypeError("[ERROR] 'nano' requires get_current_dir function")
      COMMANDS["nano"] = lambda cmd: nano(cmd, get_current_dir())


def nano(cmd, current):
    if len(cmd) < 2:
        print("\n[ERROR] Use: nano <file>")
        return

    name = cmd[1]
    old = current.get(name, "")

    if isinstance(old, dict):
        print(f"\n[ERROR] {name} is a directory.")
        return

    lines = old.splitlines()
    print(f"\nGNU nano fake - {name}")
    print("Commands: .wq save | .q cancel | .p preview | .clear empty")
    print("-" * 40)

    if lines:
        for i, line in enumerate(lines, 1):
            print(f"{i:>3}  {line}")
        print("-" * 40)

    while True:
        line = input(f"{len(lines) + 1:>3}> ")

        if line == ".q":
            print("[OK] Cancelled.")
            return
        if line == ".wq":
            current[name] = "\n".join(lines)
            print(f"[OK] Saved {len(lines)} lines.")
            return
        if line == ".p":
            print("\n".join(lines) or "[empty]")
            continue
        if line == ".clear":
            lines.clear()
            print("[OK] Cleared.")
            continue

        lines.append(line)