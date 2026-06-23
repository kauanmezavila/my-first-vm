def main_call(COMMANDS, MANIFEST=None, get_current_dir=None):
    if get_current_dir is None:
        raise TypeError("[ERROR] 'tree' requires get_current_dir function")
    COMMANDS["tree"] = lambda cmd=None: tree(get_current_dir())

def tree(node, prefix="", root=True):
    dirs = 0
    files = 0

    if root:
        print(".")

    items = list(node.items())

    for i, (name, value) in enumerate(items):
        last = i == len(items) - 1
        branch = "└── " if last else "├── "

        print(prefix + branch + name)

        if isinstance(value, dict):
            dirs += 1
            extension = "    " if last else "│   "
            d, f = tree(value, prefix + extension, root=False)
            dirs += d
            files += f
        else:
            files += 1

    if root:
        print(f"\n{dirs} directories, {files} files")

    return dirs, files
