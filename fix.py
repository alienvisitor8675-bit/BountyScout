import datetime

class BountyItem:
    def __init__(self, title, repo, comments, last_updated):
        self.title = title
        self.repo = repo
        self.comments = comments
        self.last_updated = last_updated

class BountyScanReport:
    def __init__(self, report_title, scan_time):
        self.report_title = report_title
        self.scan_time = scan_time
        self.items = []

    def populate(self, item):
        self.items.append(item)

    def display(self):
        print("### Active Bounty Scan Results")
        print(f"**Scan Time:** {self.scan_time}")
        print(f"#### {self.report_title}")
        for idx, item in enumerate(self.items, 1):
            print(f"#### {idx}. [{item.title}]")
            print(f"- **Repository:** [{item.repo}]")
            print(f"- **Comments:** {item.comments}")
            print(f"- **Last Updated:** {item.last_updated}")

def main():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report = BountyScanReport("🎯 Bounty Alert: 8 New Opportunityies found", now)

    report.populate(BountyItem("[🎯 Bounty Alert: 6 New Opportunityies found]", "freedom-winds/BountyScout", 0, "2026-08-16T14:20:09Z"))
    report.populate(BountyItem("[[radar] SN open bounty 2026-08-16T14:18]", "relayhop/ClaudeEarnSelf-runtime", 0, "2026-08-16T14:18:24Z"))
    report.populate(BountyItem("[TLA - Avatar: The Last Airbender Set Card Implementation Tracking]", "magefree/mage", 7, "2026-08-16T14:16:27Z"))
    report.populate(BountyItem("[[radar] SN open bounty 2026-08-16T13:58]", "relayhop/ClaudeEarnSelf-runtime", 1, "2026-08-16T14:10:41Z"))
    report.populate(BountyItem("[[radar] SN open bounty 2026-08-16T14:00]", "relayhop/sn-monetization-runtime", 0, "2026-08-16T14:00:17Z"))
    report.populate(BountyItem("[[Bug]: Spawn on first join]", "BeestoXd/UltimateDonutSMP", 0, "2026-08-16T14:00:17Z"))
    report.populate(BountyItem("[Bug - AI Model Hallucinates Language Switching – Replies in Chinese Despite User Using English]", "deepseek-ai/DeepSeek-V3", 2, "2026-08-16T13:57:25Z"))
    report.populate(BountyItem("[@kleros/scout-site-1.3.9.tgz: 113 vulnerabilities (highest severity is: 9.8)]", "kleros/scout-snap", 0, "2026-08-16T13:56:52Z"))

    report.display()

main()