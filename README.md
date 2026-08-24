# gambling-sites-ph

A Pi-hole blocklist of Philippine online gambling / betting sites.

Seed apex domains are listed in [`sites.txt`](sites.txt). Every subdomain on file for each apex is discovered passively via [Certificate Transparency](https://crt.name/) logs, so newly issued certificates for game servers, CDNs, payment callbacks, etc. get picked up automatically.

## Blocklists

| File | Format | Entries | Raw URL |
|------|--------|---------|---------|
| `hostfiles/hosts.txt` | hosts (`0.0.0.0 domain`) | 6873 | https://raw.githubusercontent.com/Terriakidesu/gambling-sites-ph/main/hostfiles/hosts.txt |
| `hostfiles/domains.txt` | plain domains, one per line | 6,873 | https://raw.githubusercontent.com/Terriakidesu/gambling-sites-ph/main/hostfiles/domains.txt |

Both formats are accepted by Pi-hole; use one or the other, not both.

## Setup (Pi-hole)

1. Open **Group Management > Adlists**
2. Add `https://raw.githubusercontent.com/Terriakidesu/gambling-sites-ph/main/hostfiles/hosts.txt`
3. Run **Tools > Update Gravity**
4. Flush your network's DNS cache if clients still resolve blocked domains

## Regenerating the lists

Requires Python 3.11+ ([uv](https://docs.astral.sh/uv/) recommended):

```sh
uv run main.py
```

This queries crt.name for every apex in `sites.txt`, deduplicates the results, and rewrites both files in `hostfiles/`.

## Disclaimer

This list is best-effort. CT-based discovery can include stale or unrelated subdomains, and operators rotate domains frequently. Review entries before deploying on a network you do not control.
