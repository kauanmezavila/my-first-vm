from pathlib import Path
import sys

BIOS_ROOT = Path(__file__).resolve().parent
PKG_ROOT = BIOS_ROOT / "src" / "pkgs"

def deploy(path):
    for root in (BIOS_ROOT, PKG_ROOT):
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))

    code_list: list[str] = []
    code: str = ""

    with open(BIOS_ROOT / path, "r", encoding="utf-8") as file:
        for line in file:
            code_list.append(line)

    code: str = "".join(code_list)
    exec(code, {"__file__": str(BIOS_ROOT / path), "__name__": "__main__"})
