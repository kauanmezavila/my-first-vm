from pathresolve import init_root_path

BIOS_ROOT = init_root_path(2)

import hashlib
import argparse
from pathlib import Path
import trafilatura

from src.pkgs.colorme import *

CACHE_DIR = Path.home() / ".cache" / "websearch"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

BRIGH_RE = BRIGHT_RED + BOLD
RE = RESET + RED

banner = f"""
 {BRIGH_RE}███████████  ███                     ███████████
{RE}░░{BRIGH_RE}███{RE}░░░░░░{BRIGH_RE}█ {RE}░░░                     {RE}░░{BRIGH_RE}███{RE}░░░░░░{BRIGH_RE}█
{RE} ░{BRIGH_RE}███{RE}   █ ░  {BRIGH_RE}████  ████████   ██████  {RE}░{BRIGH_RE}███{RE}   █ ░   {BRIGH_RE}██████  █████ █████
{RE} ░{BRIGH_RE}███████{RE}   ░░{BRIGH_RE}███ {RE}░░{BRIGH_RE}███{RE}░░{BRIGH_RE}███ {BRIGH_RE}███{RE}░░{BRIGH_RE}███ {RE}░{BRIGH_RE}███████{RE}    {BRIGH_RE}███{RE}░░{BRIGH_RE}███{RE}░░{BRIGH_RE}███ {RE}░░{BRIGH_RE}███
{RE} ░{BRIGH_RE}███{RE}░░░{BRIGH_RE}█{RE}    ░{BRIGH_RE}███{RE}  ░{BRIGH_RE}███ {RE}░░░ ░{BRIGH_RE}███████{RE}  ░{BRIGH_RE}███{RE}░░░{BRIGH_RE}█{RE}   ░{BRIGH_RE}███ {RE}░{BRIGH_RE}███ {RE}░░░{BRIGH_RE}█████{RE}░
{RE} ░{BRIGH_RE}███{RE}  ░     ░{BRIGH_RE}███  ░{BRIGH_RE}███     ░{BRIGH_RE}███{RE}░░░   ░{BRIGH_RE}███{RE}  ░    ░{BRIGH_RE}███ ░{BRIGH_RE}███  ███{RE}░░░{BRIGH_RE}███
 {BRIGH_RE}█████       █████ █████    {RE}░░{BRIGH_RE}██████  █████      {RE}░░{BRIGH_RE}██████  █████ █████
{RE}░░░░░       ░░░░░ ░░░░░      ░░░░░░  ░░░░░        ░░░░░░  ░░░░░ ░░░░░{WHITE}

{BOLD}Mozzilla {BRIGHT_RED}FireFox{WHITE} © 2002 {BOLD}|{RESET} Created by {BRIGH_RE}Dave Hyatt{RESET}, {BRIGH_RE}Joe Hewitt{RESET} and {BRIGH_RE}Blake Ross{RESET}
"""

def main_call(COMMANDS, MANIFEST=None, get_current_dir=None):
    COMMANDS["firefox"] = lambda cmd=None: firefox(cmd)


class FirefoxArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)

    def exit(self, status=0, message=None):
        if message:
            print(message, end="")
        if status != 0:
            raise ValueError("Invalid arguments.")
        raise SystemExit(status)

def extract(url: str, max_chars: int = 5000) -> str:
    cache_key = hashlib.md5(f"{url}:{max_chars}".encode()).hexdigest()[:12]

    cache_file = CACHE_DIR / f"{cache_key}.txt"

    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")

    try:
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return "[ERROR] Não foi possível baixar a página."

        text = trafilatura.extract(
            downloaded,
            url=url,
            favor_precision=True,
            include_comments=False,
            include_tables=False,
        )

        if not text:
            return "[ERROR] Não foi possível extrair o conteúdo."

        text = text[:max_chars]

        cache_file.write_text(text, encoding="utf-8")
        return text

    except Exception as e:
        return f"[ERROR] {e}"


def search(query: str, limit: int = 10) -> list[dict]:
    from ddgs import DDGS

    results: list[dict] = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=limit):
            results.append(
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "body": r.get("body", ""),
                }
            )
    return results


def firefox(cmd=None) -> list[dict]:
    parser = FirefoxArgumentParser(
        prog="firefox",
        description="Search the web and extract page content",
        add_help=False,
        usage="firefox [-h] [-n LIMIT] [--max-per-page CHARS] [query]",
    )
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("query", nargs="?")
    parser.add_argument("-n", "--limit", type=int, default=1, metavar="LIMIT")
    parser.add_argument("--max-per-page", type=int, default=3000, metavar="CHARS")
    parser.epilog = (
        "Examples:\n"
        "  firefox cats\n"
        "  firefox -n 5 cats\n"
        "  firefox --max-per-page 5000 cats\n"
    )

    args_list = [] if cmd is None else list(cmd)
    if args_list and args_list[0] == "firefox":
        args_list = args_list[1:]
    try:
        args = parser.parse_args(args_list)
    except (ValueError, argparse.ArgumentError) as exc:
        print(f"firefox: error: {exc}")
        print("Try 'firefox --help' for usage.")
        return []

    if args.help:
        parser.print_help()
        return []
    if args.limit < 1:
        print("firefox: error: limit must be at least 1")
        return []
    if args.max_per_page < 1:
        print("firefox: error: max-per-page must be at least 1")
        return []

    query = args.query or input("Search: ").strip()
    if not query:
        print("firefox: error: no search query specified")
        return []

    print(banner)
    print(f"\n/{'=' * 68}\\")
    print(fr"| {query:^61} @\   |")
    print("\\" + "=" * 68 + "/")

    results = search(query, args.limit)

    for i, r in enumerate(results, start=1):
        content = extract(r["url"], args.max_per_page)
        r["content"] = content

        print(f"\n[{i}] {r['title'] or 'Untitled'}")
        print("-" * 70)
        print(f"URL: {r['url']}")
        print(f"\n{content or 'No content finded.'}")
        print("\n" + "=" * 70)

    return results

