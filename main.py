import sys
import time
from pathlib import Path

import requests

API_URL = "https://crt.name/v1/search"
SITES_FILE = Path("sites.txt")
OUTPUT_DIR = Path("hostfiles")
OUTPUT_FILE = OUTPUT_DIR / "hosts.txt"
DOMAINS_FILE = OUTPUT_DIR / "domains.txt"


def main() -> None:
    if not SITES_FILE.exists():
        print(f"[!] {SITES_FILE} not found", file=sys.stderr)
        sys.exit(1)

    with SITES_FILE.open("r", encoding="utf-8") as f:
        sites = [line.strip() for line in f if line.strip()]

    if not sites:
        print("[!] No sites found in sites.txt", file=sys.stderr)
        sys.exit(1)

    print(f"[+] Loaded {len(sites)} sites from {SITES_FILE}")

    hostnames: set[str] = set()

    for site in sites:
        apex = site.strip().lower()
        if not apex:
            continue

        print(f"[*] Querying {apex} ...")
        try:
            # crt.name expects ?apex=example.com (plain text newline-separated)
            res = requests.get(API_URL, params={"apex": apex}, timeout=30)
        except requests.RequestException as exc:
            print(f"[!] Error fetching {apex}: {exc}", file=sys.stderr)
            continue

        if res.ok:
            lines = [line.strip() for line in res.text.strip().split("\n") if line.strip()]
            # deduplicate via set, keep lowercase normalized
            before = len(hostnames)
            hostnames.update(lines)
            added = len(hostnames) - before
            print(f"[+] {apex}: found {len(lines)} hostnames ({added} new, {len(hostnames)} total)")
        else:
            print(f"[!] Error fetching {apex}: HTTP {res.status_code} - {res.text[:500].strip()}", file=sys.stderr)
            print(f"[!] Failed to fetch {apex} (HTTP {res.status_code})")

        # be nice to the API - avoid hammering CT log
        time.sleep(0.5)

    # sort for deterministic output: alphabetical
    sorted_hosts = sorted(hostnames, key=lambda x: x.lower())

    print(f"\n[+] Total unique hostnames: {len(sorted_hosts)}")
    for host in sorted_hosts:
        print(host)

    # write output files
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # domains list (one per line)
    with DOMAINS_FILE.open("w", encoding="utf-8", newline="\n") as out:
        for host in sorted_hosts:
            out.write(host + "\n")
    print(f"[+] Wrote {len(sorted_hosts)} domains to {DOMAINS_FILE}")

    # hosts file format (0.0.0.0 host)
    with OUTPUT_FILE.open("w", encoding="utf-8", newline="\n") as out:
        out.write("# Hosts blocklist generated from crt.name\n")
        out.write(f"# Source: {', '.join(sites)}\n")
        out.write(f"# Total: {len(sorted_hosts)} hostnames\n\n")
        for host in sorted_hosts:
            out.write(f"0.0.0.0 {host}\n")
    print(f"[+] Wrote hosts file to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
