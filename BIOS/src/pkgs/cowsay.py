def main_call(COMMANDS, MANIFEST=None):
    COMMANDS["cowsay"] = cowsay

def cowsay(cmd):
    phrase = " ".join(cmd[1:])
    leny = len(phrase)

    print(rf""" /{"=" * leny}\
 |{phrase}|
 \{"=" * leny}/
             \  ^__^
              \ (oo)\_______
               \(__)\       )\/\
                    ||----w |
                    ||     ||
""")
