from textwrap import wrap

def main_call(COMMANDS, MANIFEST=None, get_current_dir=None):
    COMMANDS["cowsay"] = cowsay


def cowsay(cmd, width=40):
    phrase = " ".join(cmd[1:])
    lines = wrap(phrase, width=width) or [""]

    max_len = max(len(line) for line in lines)

    print(f" /{'=' * max_len}\\")
    for line in lines:
        print(f" |{line.ljust(max_len)}|")
    print(f" \\{'=' * max_len}/")
    print(r"""             \  ^__^
              \ (oo)\_______
               (__)\       )\/\
                    ||----w |
                    ||     ||
""")
