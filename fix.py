from dataclasses import dataclass, field
from typing import List

@dataclass
class BountyItem:
    title: str
    repo: str
    number: int
    comments: int
    last_updated: str

@dataclass
class ActiveBountyScan:
    scan_time: str
    items: List[BountyItem] = field(default_factory=list)

def build_scan(scan_time: str) -> ActiveBountyScan:
    s = ActiveBountyScan(scan_time=scan_time)
    s.items = [
        BountyItem(title="[radar] SN open bounty 2026-08-16T11:15", repo="relayhop/ClaudeEarnSelf-runtime", number=648, comments=0, last_updated="2026-08-16T11:15:48Z"),
        BountyItem(title="Avatar's blanket unoptimized prop defeats Next.js image optimization for every avatar in the app", repo="MergeFi/frontend", number=79, comments=1, last_updated="2026-08-16T11:13:22Z"),
        BountyItem(title="[radar] SN open bounty 2026-08-16T10:58", repo="relayhop/ClaudeEarnSelf-runtime", number=647, comments=0, last_updated="2026-08-16T10:58:09Z"),
        BountyItem(title="[radar] SN open bounty 2026-08-16T10:51", repo="relayhop/sn-monetization-runtime", number=392, comments=0, last_updated="2026-08-16T10:51:05Z"),
        BountyItem(title="Desktop AppImage tries to connect to Tor without asking; no way to disable it (JIO/India ISP blocks Tor)", repo="vitorpamplona/amethyst", number=3933, comments=0, last_updated="2026-08-16T10:48:01Z"),
        BountyItem(title="ZM needs a websocket", repo="ZoneMinder/zoneminder", number=2875, comments=10, last_updated="2026-08-16T10:33:18Z"),
    ]
    return s

if __name__ == "__main__":
    main = build_scan("2026-08-16 11:17 UTC")
    for i, item in enumerate(main.items, 1):
        print(f"{i}. [{item.title}]({item.repo})")