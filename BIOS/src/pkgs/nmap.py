from pathresolve import init_root_path

BIOS_ROOT = init_root_path(2)

import argparse
import errno
import socket
import time
from typing import NoReturn

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.pkgs.colorme import *


class NmapArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)

    def exit(self, status=0, message=None) -> NoReturn:
        if message:
            print(message, end="")
        if status != 0:
            raise ValueError("Invalid arguments.")
        raise SystemExit(status)


def parse_ports(value):
    ports = set()

    try:
        for part in value.split(","):
            part = part.strip()

            if not part:
                raise ValueError

            if "-" in part:
                pieces = part.split("-")
                if len(pieces) != 2:
                    raise ValueError

                first, last = map(int, pieces)

                if not (1 <= first <= last <= 65535):
                    raise ValueError

                ports.update(range(first, last + 1))
            else:
                port = int(part)

                if not 1 <= port <= 65535:
                    raise ValueError

                ports.add(port)

    except ValueError:
        raise argparse.ArgumentTypeError(
            "ports must be numbers or ranges, e.g. 22,80,443,8000-8010"
        )

    if not ports:
        raise argparse.ArgumentTypeError("empty port list")

    return sorted(ports)


def main_call(COMMANDS, MANIFEST, get_current_dir=None):
    COMMANDS["nmap"] = lambda cmd=None: nmap(MANIFEST, cmd)


def nmap(MANIFEST, cmd=None):
    parser = NmapArgumentParser(
        prog="nmap",
        description="Network exploration tool",
        add_help=False,
        usage="nmap [-h] [-p PORTS] [-T TIMING] [--timeout SECONDS] [target]",
    )

    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("target", nargs="?")
    parser.add_argument("-p", "--ports", type=parse_ports, default=None)
    parser.add_argument(
        "-T", dest="timing", type=int, choices=range(1, 6), default=3, metavar="0-5"
    )
    parser.add_argument("--timeout", type=float, default=0.5, metavar="SECONDS")

    parser.epilog = (
        "Examples:\n"
        "  nmap 192.168.1.10\n"
        "  nmap -p 22,80,443 192.168.1.10\n"
        "  nmap -p 1-1024 -T 4 192.168.1.10\n"
    )

    if cmd is None:
        args_list = []
    else:
        args_list = list(cmd)

        if args_list and args_list[0] == "nmap":
            args_list = args_list[1:]

    try:
        args = parser.parse_args(args_list)
    except (ValueError, argparse.ArgumentError) as exc:
        print(f"nmap: error: {exc}")
        print("Try 'nmap --help' for usage.")
        return

    if args.help:
        parser.print_help()
        return

    if args.timeout <= 0 or args.timeout > 30:
        print("nmap: error: timeout must be greater than 0 and at most 30 seconds")
        return

    target = args.target

    if not target:
        target = input("Target: ").strip()

    if not target:
        print("nmap: error: no target specified")
        return

    ports = args.ports or list(range(1, 1025))

    workers = {1: 10, 2: 25, 3: 50, 4: 100, 5: 200}[args.timing]

    try:
        addresses = socket.getaddrinfo(
            target, None, family=socket.AF_INET, type=socket.SOCK_STREAM
        )
        ip = addresses[0][4][0]
    except (socket.gaierror, IndexError, OSError):
        print(f"Failed to resolve '{target}'.")
        return

    started = time.perf_counter()
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")

    print()
    print(f"Starting Nmap 7.98 ( https://nmap.org ) at {timestamp}")
    print(f"Nmap scan report for {target} ({ip})")
    print(f"Scanning {len(ports)} TCP ports")
    print()

    def scan_tcp(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(args.timeout)
                result = sock.connect_ex((ip, port))

            if result == 0:
                try:
                    service = socket.getservbyport(port, "tcp")
                except OSError:
                    service = "unknown"

                return port, "open", service

            if result == errno.ECONNREFUSED:
                return port, "closed", None

            if result in (
                errno.ETIMEDOUT,
                errno.EHOSTUNREACH,
                errno.ENETUNREACH,
                errno.EACCES,
            ):
                return port, "filtered", None

            return port, "unknown", None

        except OSError:
            return port, "unknown", None

    results = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(scan_tcp, port): port for port in ports}

        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception:
                port = futures[future]
                results.append((port, "unknown", None))

    results.sort(key=lambda item: item[0])
    elapsed = time.perf_counter() - started

    counts = {"open": 0, "closed": 0, "filtered": 0, "unknown": 0}

    for _, state, _ in results:
        counts[state] += 1

    if counts["open"] or counts["closed"]:
        print("Host is up.")
    elif counts["filtered"]:
        print("Host status: probes filtered; availability uncertain.")
    else:
        print("Host status: unknown; no conclusive TCP response.")

    hidden = counts["closed"] + counts["filtered"] + counts["unknown"]

    if hidden:
        print(
            f"Not shown: {hidden} scanned TCP ports "
            f"(closed: {counts['closed']}, "
            f"filtered: {counts['filtered']}, "
            f"unknown: {counts['unknown']})"
        )

    print()
    print("PORT     STATE     SERVICE")

    for port, state, service in results:
        if state == "open":
            print(f"{port}/tcp".ljust(9) + f"{state:<10}{service}")

    print()
    print(f"Nmap done: 1 IP address ({ip}) scanned in " f"{elapsed:.2f} seconds")
