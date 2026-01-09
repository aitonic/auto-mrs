#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import ipaddress
import os
import sys
import urllib.request
from datetime import datetime, timezone

RIPESTAT_URL = "https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS6507"

def http_get_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "riot-as6507-mrs/1.0 (GitHub Actions)"
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def sort_key(prefix: str):
    net = ipaddress.ip_network(prefix, strict=False)
    # IPv4 first, then IPv6; stable numeric ordering
    return (net.version, int(net.network_address), net.prefixlen)

def main() -> int:
    data = http_get_json(RIPESTAT_URL)

    prefixes = data.get("data", {}).get("prefixes", [])
    cidrs = sorted({p["prefix"] for p in prefixes if "prefix" in p}, key=sort_key)

    os.makedirs("output", exist_ok=True)

    # 规则集（text ipcidr）：每行一个 CIDR
    with open("output/riot_as6507_ipcidr.txt", "w", encoding="utf-8") as f:
        for c in cidrs:
            f.write(c + "\n")

    meta = {
        "source": "RIPEstat announced-prefixes",
        "source_url": RIPESTAT_URL,
        "asn": "AS6507",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "prefix_count": len(cidrs),
        "prefixes": cidrs,
    }
    with open("output/riot_as6507.meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Fetched {len(cidrs)} prefixes from RIPEstat for AS6507.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
