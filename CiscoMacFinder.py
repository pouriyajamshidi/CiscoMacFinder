#!/usr/bin/env python3

import argparse
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from getpass import getpass
from pathlib import Path

import yaml
from netmiko import ConnectHandler

BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

MAC_COMMAND = "show mac address-table"


@dataclass(frozen=True)
class Switch:
    name: str
    mgmt_ip: str
    port: int = 22


@dataclass(frozen=True)
class Hit:
    switch: str
    port: str
    vlan: str
    mac_type: str


def say(message: str, color: str = "") -> None:
    print(f"{color}{message}{RESET}", flush=True)


def to_cisco_mac(mac: str) -> str:
    digits = re.sub(r"[.:-]", "", mac).lower()
    if not re.fullmatch(r"[0-9a-f]{12}", digits):
        raise ValueError(f"invalid MAC address: {mac}")
    return f"{digits[:4]}.{digits[4:8]}.{digits[8:]}"


def load_sites(path: Path) -> dict[str, list[Switch]]:
    sites = yaml.safe_load(path.read_text())
    return {name: [Switch(**sw) for sw in switches] for name, switches in sites.items()}


def fetch_mac_table(switch: Switch, username: str, password: str) -> str:
    device = {
        "device_type": "cisco_ios",
        "ip": switch.mgmt_ip,
        "port": switch.port,
        "username": username,
        "password": password,
    }

    with ConnectHandler(**device) as connection:
        return connection.send_command(MAC_COMMAND, read_timeout=60)


def search_table(table: str, mac: str, switch: Switch) -> list[Hit]:
    hits = []
    for line in table.splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[1].lower() == mac:
            hits.append(Hit(switch.name, fields[-1], fields[0], fields[2]))
    return hits


def scan_site(
    switches: list[Switch],
    mac: str,
    username: str,
    password: str,
    workers: int,
) -> list[Hit]:
    found: list[Hit] = []

    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = {
            pool.submit(fetch_mac_table, switch, username, password): switch
            for switch in switches
        }

        for future in as_completed(pending):
            switch = pending[future]
            try:
                table = future.result()
            except Exception as error:
                say(f"[-] Could not connect to {switch.name}: {error}", RED)
                continue

            hits = search_table(table, mac, switch)
            if not hits:
                say(f"[-] MAC not found on {switch.name}", YELLOW)
                continue

            found.extend(hits)
            for hit in hits:
                say(
                    f" |---> [+] Found [{mac}] on {hit.switch} port {hit.port},"
                    f" VLAN {hit.vlan} ({hit.mac_type})",
                    BOLD + GREEN,
                )

    return sorted(found, key=lambda hit: (hit.switch, hit.port))


def lookup_mac(
    mac: str,
    sites: dict[str, list[Switch]],
    username: str,
    password: str,
    workers: int,
) -> list[Hit]:
    say(f"[+] Searching for: {BLUE}{mac}", BOLD + GREEN)

    for site, switches in sites.items():
        say(f"[+] Looking up {site} site on {len(switches)} device(s).", BOLD + GREEN)
        print("-" * 50)

        found = scan_site(switches, mac, username, password, workers)
        if found:
            return found

    return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find a MAC address on Cisco switches."
    )
    parser.add_argument("mac", help="MAC address in Cisco, Linux or Windows notation")
    parser.add_argument("-s", "--switches", type=Path, default=Path("switches.yml"))
    parser.add_argument("-u", "--username", default=os.getenv("CISCO_USERNAME"))
    parser.add_argument(
        "-w", "--workers", type=int, default=10, help="switches polled in parallel"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        mac = to_cisco_mac(args.mac)
        sites = load_sites(args.switches)
    except (ValueError, OSError, yaml.YAMLError, TypeError) as error:
        say(f"[X] {error}", RED)
        return 2

    username = args.username or input("[+] Username: ")
    password = os.getenv("CISCO_PASSWORD") or getpass("[+] Password: ")

    found = lookup_mac(mac, sites, username, password, args.workers)

    if not found:
        say(f"[-] {mac} was not found", BOLD + RED)
        return 1

    say(
        f"[+] MAC was seen on {len({hit.switch for hit in found})} switch(es)",
        BOLD + GREEN,
    )
    for hit in found:
        say(f"\t{hit.switch} {hit.port}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
