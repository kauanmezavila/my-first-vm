import argparse
import requests
import time
import socket
import ipaddress
import statistics

def main_call(COMMANDS, MANIFEST=None, get_current_dir=None):
    COMMANDS["ping"] = lambda cmd=None: ping_command(cmd)


def ping_command(cmd=None):
    parser = argparse.ArgumentParser(prog="ping", add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    family = parser.add_mutually_exclusive_group()
    family.add_argument("-4", dest="version", action="store_const", const="IPv4")
    family.add_argument("-6", dest="version", action="store_const", const="IPv6")
    parser.add_argument("-c", "--count", type=int, default=None)
    parser.add_argument("host", nargs="?")

    args_list = list(cmd or [])
    if args_list and args_list[0] == "ping":
        args_list = args_list[1:]

    try:
        args = parser.parse_args(args_list)
    except SystemExit:
        print("Usage: ping [-4 | -6] [-c COUNT] HOST")
        return

    if args.help:
        print("Usage: ping [-4 | -6] [-c COUNT] HOST")
        print("Checks HTTPS response time; this is not an ICMP ping.")
        return
    if not args.host:
        print("ping: missing host (try 'ping --help')")
        return
    if args.count is not None and args.count < 1:
        print("ping: count must be greater than zero")
        return

    ping(args.host, args.version, args.count)

def identifyHost(value: str) -> str:
    try:
        ip = ipaddress.ip_address(value)
        return f"IPv{ip.version}"
    except ValueError:
        try:
            socket.getaddrinfo(value, None)
            return "DOMAIN"
        except socket.gaierror:
            return "INVALID"


def urlToIP(url):
    ipv4, ipv6 = set(), set()

    for r in socket.getaddrinfo(url, None):
        if r[0] == socket.AF_INET:
            ipv4.add(r[4][0])
        elif r[0] == socket.AF_INET6:
            ipv6.add(r[4][0])

    return ipv4, ipv6


def ping(entry, version=None, count=None):
    if not isinstance(entry, str) or not entry.strip():
        print("Invalid host")
        return
    entry = entry.strip()
    entryType = identifyHost(entry)

    if entryType == "INVALID":
        print("Invalid host")
        return

    if entryType in ("IPv4", "IPv6"):
        ip = ipaddress.ip_address(entry)

        if version and version != entryType:
            print(f"Address is not {version}")
            return

        address = str(ip)
        host = address
        family = socket.AF_INET if ip.version == 4 else socket.AF_INET6

    else:
        try:
            ipv4, ipv6 = urlToIP(entry)
        except (socket.gaierror, OSError):
            print(f"Could not resolve host: {entry}")
            return

        if version == "IPv4":
            addresses = ipv4
            family = socket.AF_INET
        elif version == "IPv6":
            addresses = ipv6
            family = socket.AF_INET6
        else:
            addresses = ipv4 or ipv6
            family = socket.AF_INET if ipv4 else socket.AF_INET6

        if not addresses:
            print(f"No {version or 'IP'} address found for {entry}")
            return

        address = sorted(addresses)[0]
        host = entry

    # Requests uses HTTPS, not ICMP. Domain URLs let requests handle DNS and TLS.
    url = f"https://{host}" if entryType == "DOMAIN" else (
        f"https://[{address}]" if family == socket.AF_INET6
        else f"https://{address}"
    )

    sentPkgs = {}
    pkgID = 0
    pkgSucess = 0
    startTotal = time.perf_counter()
    pkg = b"\x00" * 56

    print(f"HTTPS probe to {entry} ({address}); {len(pkg)} data bytes")

    try:
        while count is None or pkgID < count:
            pkgID += 1

            try:
                start = time.perf_counter()

                response = requests.get(
                    url,
                    data=pkg,
                    timeout=5,
                    headers={"Connection": "close"},
                    stream=True
                )

                tim = (time.perf_counter() - start) * 1000
                response.close()

                sentPkgs[pkgID] = tim
                pkgSucess += 1

                print(f"HTTPS response from {address}: seq={pkgID} time={tim:.2f} ms")

            except requests.RequestException:
                print(f"Request failed for {address}")

            if count is None or pkgID < count:
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        totalTime = (time.perf_counter() - startTotal) * 1000
        lost = pkgID - pkgSucess
        loss = lost / pkgID * 100 if pkgID else 0

        print(f"\n--- {entry} HTTPS probe statistics ---")
        print(
            f"{pkgID} probes sent, {pkgSucess} responses received, "
            f"{loss:.1f}% failed, time {totalTime:.0f}ms"
        )

        if sentPkgs:
            times = list(sentPkgs.values())

            minimum = min(times)
            average = statistics.mean(times)
            maximum = max(times)
            mdev = statistics.pstdev(times)

            print(
                f"response time min/avg/max/mdev = "
                f"{minimum:.3f}/{average:.3f}/"
                f"{maximum:.3f}/{mdev:.3f} ms"
            )
