from pathresolve import init_root_path
BIOS_ROOT = init_root_path(2)

from VMs.Debian.init_pkg import MOUNT_INSTRUCTIONS, MANIFEST

distro = MANIFEST["distro"]

code_list: list[str] = []
code: str = ""

with open(BIOS_ROOT / MOUNT_INSTRUCTIONS["source"], "r", encoding="utf-8") as file:
    for line in file:
        code_list.append(line)

code: str = "".join(code_list)
exec(code)
