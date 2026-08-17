from dataclasses import dataclass, field
from typing import List

@dataclass
class BountyScanItem:
    index: int
    title: str
    repo: str
    comments: int
    last_updated: str

@dataclass
class ActiveBountyScan:
    scan_time: str
    total_items: int
    items: List[BountyScanItem] = field(default_factory=list)

    def render(self):
        for i in range(1, self.total_items + 1):
            item = self.items[i - 1]
            print(f"{i}. [{item.title}]")
            print(f"   - Repository: {item.repo}")
            print(f"   - Comments: {item.comments}")
            print(f"   - Last Updated: {item.last_updated}")

    def __init__(self):
        self.scan_time = "2026-08-17 04:39 UTC"
        self.total_items = 15
        self.items = [
            BountyScanItem(index=1, title="🎯 Bounty Alert: 14 New Opportunityies found", repo="freedom-winds/BountyScout", comments=0, last_updated="2026-08-17T04:38:59Z"),
            BountyScanItem(index=2, title="[radar] SN open bounty 2026-08-17T04:25", repo="relayhop/sn-monetization-runtime", comments=0, last_updated="2026-08-17T04:25:56Z"),
            BountyScanItem(index=3, title="🚨 Bounty Governo — Protezione civile e resilienza", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:25:26Z"),
            BountyScanItem(index=4, title="📊 Bounty Governo — Trasparenza e dati pubblici", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:25:20Z"),
            BountyScanItem(index=5, title="♿ Bounty Governo — Accessibilità e inclusione", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:25:15Z"),
            BountyScanItem(index=6, title="🎓 Bounty Governo — Istruzione e formazione", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:25:12Z"),
            BountyScanItem(index=7, title="🏥 Bounty Governo — Sanità e servizi al cittadino", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:25:08Z"),
            BountyScanItem(index=8, title="🚆 Bounty Governo — Mobilità e infrastrutture", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:25:00Z"),
            BountyScanItem(index=9, title="🌱 Bounty Governo — Ambiente, energia e sostenibilità", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:24:56Z"),
            BountyScanItem(index=10, title="🔐 Bounty Governo — Cybersecurity e sicurezza dei servizi", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:24:48Z"),
            BountyScanItem(index=11, title="💻 Bounty Governo — Digitalizzazione e interoperabilità", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:24:44Z"),
            BountyScanItem(index=12, title="🏛️ Bounty Governo — Servizi pubblici e semplificazione", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:24:35Z"),
            BountyScanItem(index=13, title="🤝 Bounty Urban Lab — Partecipazione civica e inclusione", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:20:48Z"),
            BountyScanItem(index=14, title="🌱 Bounty Urban Lab — Verde, sostenibilità e resilienza urbana", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:20:44Z"),
            BountyScanItem(index=15, title="🏙️ Bounty Urban Lab — Rigenerazione e spazio pubblico", repo="MyZubster-Ecosystem/myzubster", comments=0, last_updated="2026-08-17T04:20:39Z"),
        ]

if __name__ == "__main__":
    report = ActiveBountyScan()
    report.render()