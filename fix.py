from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class BountyNode:
    index: int
    title: str
    repository: str
    comments: int
    last_updated: str

@dataclass
class BountyScan:
    scan_time: str
    total_nodes: int
    items: List[BountyNode]

    def generate_report(self) -> str:
        lines = []
        lines.append(f"Title: [$2026.0] 🎯 Bounty Alert: {self.total_nodes} Found")
        lines.append("Details: ### Active Bounty Scan Results")
        lines.append(f"**Scan Time:** {self.scan_time} UTC")
        lines.append("")

        for node in self.items:
            lines.append(f"#### {node.index}. [{node.title}]")
            lines.append(f"- **Repository:** [{node.repository}]")
            lines.append(f"- **Comments:** {node.comments}")
            lines.append(f"- **Last Updated:** {node.last_updated}")
            lines.append("")
        return "\n".join(lines)

    def run(self):
        report = self.generate_report()
        print(report)

def main():
    now = "2026-08-16T12:34:30Z"
    
    items = [
        BountyNode(1, "🎯 Bounty Alert: 6 New Opportunityies found", "freedom-winds/BountyScout", 0, "2026-08-16T12:34:30Z"),
        BountyNode(2, "[VULN] Security Alert for node-forge", "SRM-Test-DEV/test-56", 0, "2026-08-16T12:30:28Z"),
        BountyNode(3, "[radar] SN open bounty 2026-08-16T12:29", "relayhop/ClaudeEarnSelf-runtime", 0, "2026-08-16T12:29:31Z"),
        BountyNode(4, "🎯 Bounty Alert: 6 New Opportunityies found", "freedom-winds/BountyScout", 1, "2026-08-16T12:18:00Z"),
        BountyNode(5, "🎯 Bounty Alert: 7 New Opportunityies found", "dev-kp-eloper/BountyScout", 1, "2026-08-16T12:15:16Z"),
        BountyNode(6, "[radar] SN open bounty 2026-08-16T11:55", "relayhop/ClaudeEarnSelf-runtime", 1, "2026-08-16T12:10:48Z"),
        BountyNode(7, "[radar] SN open bounty 2026-08-16T12:00", "relayhop/sn-monetization-runtime", 1, "2026-08-16T12:03:24Z"),
    ]

    session = BountyScan(scan_time=now, total_nodes=len(items), items=items)
    session.run()

if __name__ == "__main__":
    main()