from pathresolve import init_root_path
BIOS_ROOT = init_root_path(2)

from src.pkgs.colorme import *
from hardware import HARDWARE

def main_call(COMMANDS, MANIFEST, get_current_dir=None):
    COMMANDS["neofetch"] = lambda: neofetch(MANIFEST)

def neofetch(MANIFEST):

    if MANIFEST["distro"] == "Debian":
        print(f"""{RED}
⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⡀⡀⠀⠀⠀⠀⡀         {RED}{MANIFEST["user"]}{WHITE}@{RED}{MANIFEST["host"]}
{RED}⠀⠀⠀⠀⠀⠀⠀⣄⢢⠑⠾⠲⢗⢧⢪⣤⡀⡀        {WHITE}------------------
{RED}⠀⠀⠀⠀⠀⡰⣺⣞⠍⠎⠊⠉⠈⠂⠃⠅⠈⡱⢮⠠⢁     {RED}OS:{WHITE} {MANIFEST["distro"]} {MANIFEST["version"]} {MANIFEST["architecture"]}
{RED}  ⠠⡠⡜⡟⡟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢄⠁⡪⡀    {RED}Kernel:{WHITE} {MANIFEST["kernel"]}
{RED}  ⡔⢩⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢡⠉⣹⠀⠀⠀ {RED}ISO:{WHITE} {MANIFEST["iso"]}
{RED}⠀⠀⠜⣻⠅⠀⠀⠀⠀⠀⢐⡀⠄⠀⠀⠀⠀⠀⠀⢘⣚⣪⠐   {RED}GPU:{WHITE} {HARDWARE["gpu"]["manufacturer"]} {HARDWARE["gpu"]["model"]} {HARDWARE["gpu"]["driver"]} [{HARDWARE["gpu"]["vram_gb"]} GB]
{RED}⠈⡀⠹⣿⠀⠀⠀⠀⠀⢐⣯⡃⠀⠀⠀⠀⠀⠀⠀⠬⢨⠏⠆   {RED}CPU: {WHITE} {HARDWARE["cpu"]["manufacturer"]} {HARDWARE["cpu"]["model"]} {HARDWARE["cpu"]["threads"]}@{HARDWARE["cpu"][f"{HARDWARE['cpu']['bios-mode']}_clock_ghz"]}GHz
{RED}⠀⠠⠸⣧⠂⠀⠀⠀⠀⠈⣝⣣⡄⠀⠀⠀⠀⣀⢄⠊⠜     {RED}Uptime: {WHITE}{MANIFEST["uptime"]}
{RED}⠀⠈⠸⢻⡇⠀⠀⠀⠀⠀⠈⠦⢌⣑⣒⣒⣉⡃⠕⠂⠁⠀⠀⠀⠀⠀
{RED}⠀⠀⠀⣲⠩⣦⠀⠀⠀⠀⠀⠀⠈⠄⠉⠁⠁⠀⠉⠈      {RESET}{BLACK}███{RED}███{GREEN}███{YELLOW}███{BLUE}███{MAGENTA}███{CYAN}███{WHITE}███{RESET}
{RED}⠀⠀⠀⠈⢏⠽⣝⢂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      {RESET}{BRIGHT_BLACK}███{BRIGHT_RED}███{BRIGHT_GREEN}███{BRIGHT_YELLOW}███{BRIGHT_BLUE}███{BRIGHT_MAGENTA}███{BRIGHT_CYAN}███{BRIGHT_WHITE}███{RESET}
{RED}⠀⠀⠀⠀⠐⠀⠉⠢⢍⣠⣀⠀⠀⠀⠀⠀⢀⠄⠀⠁
{RED}⠀⠀⠀⠀⠀⠀⠀⠈⠁⠌⠁⠉⠹⠫⠁⠁⠀⠀⠀⠀ {RESET}
""")

    if MANIFEST["distro"] == "Ubuntu":
        print(f"""{RED}
{RED}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀        {RED}{MANIFEST["user"]}{WHITE}@{RED}{MANIFEST["host"]}
{RED}⠀⠀⠀⠀⠀⠀⢀⣤⣴⣾⢿⣻⢯⣿⡽⣯⣟⣿⣳⣦⣄⡀⠀⠀⠀⠀⠀⠀        {WHITE}------------------
{RED}⠀⠀⠀⠀⣠⣾⣟⣯⣟⣾⣟⣯⣿⣳⡿⣯⣟⡾⠹⠷⣻⣟⣧⣄⠀⠀⠀⠀        {RED}OS:{WHITE} {MANIFEST["distro"]} {MANIFEST["version"]} {MANIFEST["architecture"]}
{RED}⠀⠀⢀⣾⣟⣾⣽⢾⣯⡷⣯⠟⠞⠙⠛⠳⢯⠀⠀⠀⢸⣯⣟⣾⣶⡀⠀⠀        {RED}Kernel:{WHITE} {MANIFEST["kernel"]}
{RED}⠀⢀⣾⣟⣾⣽⡾⣟⠗⠉⢷⡀⠀⣀⡀⠀⠈⠳⠤⠴⣿⣻⢾⣻⣞⣷⡄⠀        {RED}ISO:{WHITE} {MANIFEST["iso"]}
{RED}⠀⣾⢿⣽⣾⣳⡿⠃⠀⠀⣨⣟⡿⣽⣻⢿⣶⣄⠀⠀⠘⣟⡿⣽⣻⣞⣷⠀        {RED}GPU:{WHITE} {HARDWARE["gpu"]["manufacturer"]} {HARDWARE["gpu"]["model"]} {HARDWARE["gpu"]["driver"]} [{HARDWARE["gpu"]["vram_gb"]} GB]
{RED}⢸⣿⣻⡞⠗⠻⣇⠀⠀⣼⣟⣾⣟⣯⢿⣻⡾⣽⣧⠀⠀⠸⣟⣯⣷⢿⡽⡇        {RED}CPU:{WHITE} {HARDWARE["cpu"]["manufacturer"]} {HARDWARE["cpu"]["model"]} {HARDWARE["cpu"]["threads"]}@{HARDWARE["cpu"][f"{HARDWARE['cpu']['bios-mode']}_clock_ghz"]}GHz
{RED}⢸⣷⣻⠀⠀⠀⢸⠆⢘⣿⢾⣳⣯⢿⣻⣽⣟⡷⣿⠶⠶⠶⢯⣷⣟⣯⡿⡇        {RED}Uptime:{WHITE} {MANIFEST["uptime"]}
{RED}⢸⣷⣻⢷⣦⣴⡏⠀⠀⢻⣯⢿⣽⣻⣟⣾⣽⣻⡝⠀⠀⢰⣿⣳⣯⢿⣽⡇
{RED}⠀⣻⣽⣟⣾⣳⡿⡄⠀⠀⢙⣯⡷⣿⣽⢾⠳⠋⠀⠀⢠⡿⣞⣷⣟⡿⡞⠀        {RESET}{BLACK}███{RED}███{GREEN}███{YELLOW}███{BLUE}███{MAGENTA}███{CYAN}███{WHITE}███{RESET}
{RED}⠀⠈⣷⢿⣽⣳⡿⣟⣦⣀⡾⠁⠀⠁⠈⠀⢠⡴⠒⠲⣿⣻⢯⣷⣻⠿⠁⠀        {RESET}{BRIGHT_BLACK}███{BRIGHT_RED}███{BRIGHT_GREEN}███{BRIGHT_YELLOW}███{BRIGHT_BLUE}███{BRIGHT_MAGENTA}███{BRIGHT_CYAN}███{BRIGHT_WHITE}███{RESET}
{RED}⠀⠀⠈⠿⣞⣯⣿⣻⣽⣻⢷⣶⣦⣤⣤⣴⢯⠀⠀⠀⣸⣟⣯⡿⡽⠁⠀⠀
{RED}⠀⠀⠀⠀⠙⢻⣾⣽⣳⣿⣻⣞⣷⣻⡾⣽⣟⣷⣴⢶⣯⣟⡗⠋⠀⠀⠀⠀
{RED}        ⠑⠻⡾⣽⣻⣾⣽⣻⣽⣾⣻⠾⠏⠃⠁⠀⠀⠀⠀⠀⠀
{RED}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠉⠉⠁⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀        {RESET}
""")