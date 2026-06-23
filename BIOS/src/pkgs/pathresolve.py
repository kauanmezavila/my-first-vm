# OQ É o PathResolve???:
# Se você for importar algum pacote padrão ou import interno de arquivos que criou
# SEMPRE use a headline:
# 
#   from pathresolve import init_root_path
#    BIOS_ROOT = init_root_path({NIVEL})
#
# Em nível coloque o numero de pastas em relação à pasta root (no caso, BIOS), um
# exemplo seria:
# 
#   BIOS/src/Debian/
#   Nível = 2
#
# E sempre coloque o caminho de import relativo à root, caso contrário da erro

def main_call(COMMANDS, MANIFEST=None, get_current_dir=None):
    COMMANDS["pathresolve"] = None

def pathresolve():
    print("[ OK ] Im probably running already where i need to")

import sys
from pathlib import Path


def init_root_path(parents):
    BIOS_ROOT = Path(__file__).resolve().parents[parents]
    if str(BIOS_ROOT) not in sys.path:
        sys.path.insert(0, str(BIOS_ROOT))
    return BIOS_ROOT
