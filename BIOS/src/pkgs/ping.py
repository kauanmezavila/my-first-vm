
import requests
import time
import socket
import ipaddress
import statistics


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


def ping(entry, version=None):
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
        ipv4, ipv6 = urlToIP(entry)

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

    # Requests uses HTTP, not ICMP.
    url = f"https://{host}" if entryType == "DOMAIN" else (
        f"https://[{address}]" if family == socket.AF_INET6
        else f"https://{address}"
    )

    sentPkgs = {}
    pkgID = 0
    pkgSucess = 0
    startTotal = time.perf_counter()
    pkg = b"\x00" * 56

    print(f"PING {entry} ({address}) {len(pkg)} data bytes")

    try:
        while True:
            pkgID += 1

            try:
                start = time.perf_counter()

                # Force the selected IP family and connect to its address.
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

                print(
                    f"{len(pkg) + 8} bytes from {address}: "
                    f"icmp_seq={pkgID} time={tim:.2f} ms"
                )

            except requests.RequestException:
                print(f"Request failed for {address}")

            time.sleep(1)

    except KeyboardInterrupt:
        totalTime = (time.perf_counter() - startTotal) * 1000
        lost = pkgID - pkgSucess
        loss = lost / pkgID * 100 if pkgID else 0

        print(f"\n--- {entry} ping statistics ---")
        print(
            f"{pkgID} packets transmitted, {pkgSucess} received, "
            f"{loss:.1f}% packet loss, time {totalTime:.0f}ms"
        )

        if sentPkgs:
            times = list(sentPkgs.values())

            minimum = min(times)
            average = statistics.mean(times)
            maximum = max(times)
            mdev = statistics.pstdev(times)

            print(
                f"rtt min/avg/max/mdev = "
                f"{minimum:.3f}/{average:.3f}/"
                f"{maximum:.3f}/{mdev:.3f} ms"
            )
