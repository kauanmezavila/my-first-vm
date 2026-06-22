from src.pkgs.colorme import *

def main_call(COMMANDS, MANIFEST):
    COMMANDS["neofetch"] = lambda: neofetch(MANIFEST)

def neofetch(MANIFEST):

    if MANIFEST["distro"] == "Debian":
        print(f"""{RED}
⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⡀⡀⠀⠀⠀⠀⡀         {RED}user{WHITE}@{RED}main
{RED}⠀⠀⠀⠀⠀⠀⠀⣄⢢⠑⠾⠲⢗⢧⢪⣤⡀⡀        {WHITE}------------------
{RED}⠀⠀⠀⠀⠀⡰⣺⣞⠍⠎⠊⠉⠈⠂⠃⠅⠈⡱⢮⠠⢁     {RED}OS:{WHITE} {MANIFEST["distro"]} {MANIFEST["version"]} {MANIFEST["architecture"]}
{RED}  ⠠⡠⡜⡟⡟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢄⠁⡪⡀    {RED}Kernel:{WHITE} {MANIFEST["kernel"]}
{RED}  ⡔⢩⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢡⠉⣹⠀⠀⠀ {RED}ISO:{WHITE} {MANIFEST["iso"]}
{RED}⠀⠀⠜⣻⠅⠀⠀⠀⠀⠀⢐⡀⠄⠀⠀⠀⠀⠀⠀⢘⣚⣪⠐        
{RED}⠈⡀⠹⣿⠀⠀⠀⠀⠀⢐⣯⡃⠀⠀⠀⠀⠀⠀⠀⠬⢨⠏⠆   {RESET}{BLACK}███{RED}███{GREEN}███{YELLOW}███{BLUE}███{MAGENTA}███{CYAN}███{WHITE}███{RESET}
{RED}⠀⠠⠸⣧⠂⠀⠀⠀⠀⠈⣝⣣⡄⠀⠀⠀⠀⣀⢄⠊⠜     {RESET}{BRIGHT_BLACK}███{BRIGHT_RED}███{BRIGHT_GREEN}███{BRIGHT_YELLOW}███{BRIGHT_BLUE}███{BRIGHT_MAGENTA}███{BRIGHT_CYAN}███{BRIGHT_WHITE}███{RESET}
{RED}⠀⠈⠸⢻⡇⠀⠀⠀⠀⠀⠈⠦⢌⣑⣒⣒⣉⡃⠕⠂⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
{RED}⠀⠀⠀⣲⠩⣦⠀⠀⠀⠀⠀⠀⠈⠄⠉⠁⠁⠀⠉⠈
{RED}⠀⠀⠀⠈⢏⠽⣝⢂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
{RED}⠀⠀⠀⠀⠐⠀⠉⠢⢍⣠⣀⠀⠀⠀⠀⠀⢀⠄⠀⠁
{RED}⠀⠀⠀⠀⠀⠀⠀⠈⠁⠌⠁⠉⠹⠫⠁⠁⠀⠀⠀⠀ {RESET}
""")
