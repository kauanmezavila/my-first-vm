import os
import time
import json

from pathresolve import init_root_path
BIOS_ROOT = init_root_path(2)

init_root_path(2)

from src.Debian.files_vm import FILES

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
