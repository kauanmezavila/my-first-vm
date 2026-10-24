from pathresolve import init_root_path

BIOS_ROOT = init_root_path(2)

import argparse
import curses
import hashlib
import textwrap
from pathlib import Path
from urllib.parse import urlparse

import trafilatura

CACHE_DIR = Path.home() / ".cache" / "websearch"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class GoogleArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)

    def exit(self, status=0, message=None):
        if message:
            print(message, end="")
        if status != 0:
            raise ValueError("Invalid arguments.")
        raise SystemExit(status)


def extract(url: str, max_chars: int = 5000) -> str:
    cache_key = hashlib.md5(f"{url}:{max_chars}".encode("utf-8")).hexdigest()[:12]
    cache_file = CACHE_DIR / f"{cache_key}.txt"

    if cache_file.exists():
        try:
            return cache_file.read_text(encoding="utf-8")
        except OSError:
            pass

    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return "[ERROR] Not able to load page."

        content = trafilatura.extract(
            downloaded,
            url=url,
            favor_precision=True,
            include_comments=False,
            include_tables=False,
        )
        if not content:
            return "[ERROR] Not able to extract content from page."

        content = content[:max_chars]
        try:
            cache_file.write_text(content, encoding="utf-8")
        except OSError:
            pass
        return content
    except Exception as exc:
        return f"[ERROR] Failed to open the page: {exc}"


def search(query: str, limit: int = 10) -> list[dict]:
    from ddgs import DDGS

    results: list[dict] = []
    with DDGS() as ddgs:
        for result in ddgs.text(query, max_results=limit):
            results.append(
                {
                    "title": result.get("title", "") or "Sem título",
                    "url": result.get("href", "") or "",
                    "body": result.get("body", "") or "",
                }
            )
    return results


def _safe_addstr(screen, y: int, x: int, text: str, attr=0, max_width=None):
    height, width = screen.getmaxyx()
    if y < 0 or y >= height or x < 0 or x >= width:
        return
    available = width - x - 1
    if max_width is not None:
        available = min(available, max_width)
    if available <= 0:
        return
    try:
        screen.addnstr(y, x, str(text).replace("\x00", ""), available, attr)
    except curses.error:
        pass


def _init_colors():
    curses.start_color()
    try:
        curses.use_default_colors()
        background = -1
    except curses.error:
        background = curses.COLOR_BLACK

    colors = {
        "blue": curses.COLOR_BLUE,
        "red": curses.COLOR_RED,
        "yellow": curses.COLOR_YELLOW,
        "green": curses.COLOR_GREEN,
        "cyan": curses.COLOR_CYAN,
        "white": curses.COLOR_WHITE,
        "magenta": curses.COLOR_MAGENTA,
    }
    for pair, name in enumerate(colors, start=1):
        try:
            curses.init_pair(pair, colors[name], background)
        except curses.error:
            pass

    return {
        "blue": curses.color_pair(1) | curses.A_BOLD,
        "red": curses.color_pair(2) | curses.A_BOLD,
        "yellow": curses.color_pair(3) | curses.A_BOLD,
        "green": curses.color_pair(4) | curses.A_BOLD,
        "cyan": curses.color_pair(5),
        "white": curses.color_pair(6),
        "magenta": curses.color_pair(7),
        "selected": curses.A_REVERSE | curses.A_BOLD,
        "muted": curses.A_DIM,
        "bold": curses.A_BOLD,
    }


def _draw_logo(screen, colors):
    _, width = screen.getmaxyx()
    logo = "Google"
    start_x = max(0, (width - len(logo)) // 2)
    logo_colors = [colors["blue"], colors["red"], colors["yellow"],
                   colors["blue"], colors["green"], colors["red"]]
    for index, char in enumerate(logo):
        _safe_addstr(screen, 0, start_x + index, char, logo_colors[index])
    _safe_addstr(screen, 1, max(0, (width - 34) // 2),
                 "SEARCH THE WEB  |  GOOGLE", colors["muted"])


def _prompt_query(screen, colors, current="") -> str:
    height, width = screen.getmaxyx()
    prompt_y = min(4, max(0, height - 2))
    prompt = "Search: "
    screen.move(prompt_y, 0)
    screen.clrtoeol()
    _safe_addstr(screen, prompt_y, 2, prompt, colors["cyan"] | curses.A_BOLD)
    curses.echo()
    try:
        curses.curs_set(1)
    except curses.error:
        pass
    try:
        raw = screen.getstr(prompt_y, min(2 + len(prompt), max(0, width - 2)), max(1, min(512, width - len(prompt) - 5)))
        entered = raw.decode("utf-8", errors="replace").strip()
    except (curses.error, UnicodeError):
        entered = ""
    finally:
        curses.noecho()
        try:
            curses.curs_set(0)
        except curses.error:
            pass
    return entered or current.strip()


def _draw_results(screen, colors, query, results, selected, scroll_top, status=""):
    screen.erase()
    height, width = screen.getmaxyx()
    _draw_logo(screen, colors)
    _safe_addstr(screen, 2, 2, f"Search: {query}", colors["cyan"] | curses.A_BOLD)
    _safe_addstr(screen, 3, 2, f"{len(results)} result(s)", colors["muted"])

    first_y = 5
    footer_rows = 2
    usable_rows = max(1, height - first_y - footer_rows)
    rows_per_result = 3
    visible_count = max(1, usable_rows // rows_per_result)
    scroll_top = max(0, min(scroll_top, max(0, len(results) - visible_count)))

    if not results:
        _safe_addstr(screen, first_y, 2, "No results found.", colors["yellow"])
    else:
        for index in range(scroll_top, min(len(results), scroll_top + visible_count)):
            result = results[index]
            y = first_y + (index - scroll_top) * rows_per_result
            attr = colors["selected"] if index == selected else colors["bold"]
            title = result.get("title") or "No title"
            url = result.get("url") or "(URL unavailable)"
            snippet = result.get("body") or "No description available."
            domain = urlparse(url).netloc or url
            _safe_addstr(screen, y, 2, f"{index + 1:>2}. {title}", attr)
            _safe_addstr(screen, y + 1, 6, domain, colors["green"] if index == selected else colors["cyan"])
            _safe_addstr(screen, y + 2, 6, snippet, colors["white"] if index == selected else 0)

    if status:
        _safe_addstr(screen, max(0, height - 2), 2, status, colors["yellow"])
    _safe_addstr(screen, max(0, height - 1), 1,
                 "↑/↓ navigate  ENTER open  / new search  R refresh  Q quit",
                 colors["muted"])
    screen.refresh()
    return visible_count


def _read_page(screen, colors, result, max_chars):
    url = result.get("url", "")
    title = result.get("title", "Page")
    screen.erase()
    height, _ = screen.getmaxyx()
    _draw_logo(screen, colors)
    _safe_addstr(screen, 2, 2, f"Opening: {title}", colors["cyan"] | curses.A_BOLD)
    _safe_addstr(screen, 3, 2, url, colors["green"])
    _safe_addstr(screen, 5, 2, "Loading content...", colors["yellow"])
    screen.refresh()

    content = extract(url, max_chars) if url else "[ERROR] Result with no URL."
    lines = []
    for paragraph in content.splitlines() or ["No content."]:
        if not paragraph.strip():
            lines.append("")
        else:
            lines.extend(textwrap.wrap(paragraph, width=78, replace_whitespace=False) or [""])

    offset = 0
    while True:
        screen.erase()
        height, width = screen.getmaxyx()
        _draw_logo(screen, colors)
        _safe_addstr(screen, 2, 2, title, colors["cyan"] | curses.A_BOLD)
        _safe_addstr(screen, 3, 2, url, colors["green"])
        content_top = 5
        content_height = max(1, height - content_top - 2)
        for row, line in enumerate(lines[offset:offset + content_height]):
            _safe_addstr(screen, content_top + row, 2, line, 0, max(1, width - 4))
        _safe_addstr(screen, max(0, height - 1), 1,
                     "↑/↓ scroll  PgUp/PgDn page  HOME start  B back",
                     colors["muted"])
        screen.refresh()

        key = screen.getch()
        if key in (ord("b"), ord("B"), 27, ord("q"), ord("Q")):
            return
        if key in (curses.KEY_DOWN, ord("j")):
            offset = min(max(0, len(lines) - content_height), offset + 1)
        elif key in (curses.KEY_UP, ord("k")):
            offset = max(0, offset - 1)
        elif key == curses.KEY_NPAGE:
            offset = min(max(0, len(lines) - content_height), offset + content_height)
        elif key == curses.KEY_PPAGE:
            offset = max(0, offset - content_height)
        elif key == curses.KEY_HOME:
            offset = 0
        elif key == curses.KEY_END:
            offset = max(0, len(lines) - content_height)


def _run_tui(screen, initial_query, limit, max_chars):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    colors = _init_colors()
    query = initial_query
    results = []
    selected = 0
    scroll_top = 0

    while True:
        if not query:
            screen.erase()
            _draw_logo(screen, colors)
            query = _prompt_query(screen, colors)
            if not query:
                return []

        screen.erase()
        _draw_logo(screen, colors)
        _safe_addstr(screen, 3, 2, f"Searching for: {query}", colors["yellow"])
        screen.refresh()
        try:
            results = search(query, limit)
            status = ""
        except Exception as exc:
            results = []
            status = f"Failed to search: {exc}"
        selected = 0
        scroll_top = 0

        while True:
            visible_count = _draw_results(screen, colors, query, results, selected, scroll_top, status)
            key = screen.getch()

            if key in (ord("q"), ord("Q"), 27):
                return results
            if key in (curses.KEY_DOWN, ord("j")) and results:
                selected = min(len(results) - 1, selected + 1)
                if selected >= scroll_top + visible_count:
                    scroll_top = selected - visible_count + 1
            elif key in (curses.KEY_UP, ord("k")) and results:
                selected = max(0, selected - 1)
                if selected < scroll_top:
                    scroll_top = selected
            elif key in (curses.KEY_HOME,):
                selected, scroll_top = 0, 0
            elif key in (curses.KEY_END,) and results:
                selected = len(results) - 1
                scroll_top = max(0, selected - visible_count + 1)
            elif key in (curses.KEY_NPAGE,) and results:
                selected = min(len(results) - 1, selected + visible_count)
                scroll_top = min(max(0, len(results) - visible_count), scroll_top + visible_count)
            elif key in (curses.KEY_PPAGE,) and results:
                selected = max(0, selected - visible_count)
                scroll_top = max(0, scroll_top - visible_count)
            elif key in (10, 13, curses.KEY_ENTER) and results:
                _read_page(screen, colors, results[selected], max_chars)
            elif key in (ord("/"), ord("s"), ord("S")):
                new_query = _prompt_query(screen, colors, query)
                if new_query:
                    query = new_query
                break
            elif key in (ord("r"), ord("R")):
                break


def main_call(COMMANDS, MANIFEST=None, get_current_dir=None):
    COMMANDS["google"] = lambda cmd=None: google(cmd)


def google(cmd=None) -> list[dict]:
    parser = GoogleArgumentParser(
        prog="google",
        description="Search the web in a terminal TUI",
        add_help=False,
        usage="google [-h] [-n LIMIT] [--max-per-page CHARS] [query]",
    )
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("query", nargs="?")
    parser.add_argument("-n", "--limit", type=int, default=10, metavar="LIMIT")
    parser.add_argument("--max-per-page", type=int, default=5000, metavar="CHARS")
    parser.epilog = (
        "TUI Shortcuts:\n"
        "  ↑/↓ or j/k   navigate through results\n"
        "  Enter        open and extract text from page\n"
        "  /            make a new search\n"
        "  R            repeat the current search\n"
        "  Q            quit\n\n"
        "Examples:\n"
        "  google linux server\n"
        "  google -n 20 python curses\n"
        "  google --max-per-page 8000 python documentation"
    )

    args_list = [] if cmd is None else list(cmd)
    if args_list and args_list[0] == "google":
        args_list = args_list[1:]

    try:
        args = parser.parse_args(args_list)
    except (ValueError, argparse.ArgumentError) as exc:
        print(f"google: error: {exc}")
        print("Use 'google --help' to see the help.")
        return []

    if args.help:
        parser.print_help()
        return []
    if args.limit < 1:
        print("google: error: limit must be at least 1")
        return []
    if args.max_per_page < 1:
        print("google: error: max-per-page must be at least 1")
        return []

    try:
        return curses.wrapper(_run_tui, args.query or "", args.limit, args.max_per_page)
    except KeyboardInterrupt:
        return []
    except curses.error as exc:
        print(f"google: error: could not initialize TUI: {exc}")
        print("Run the command in an interactive terminal.")
        return []


if __name__ == "__main__":
    google()
