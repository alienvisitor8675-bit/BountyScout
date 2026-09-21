```python
def format_bounties(bounty_list):
    if not bounty_list:
        return "No new bounties found."
    formatted = f"### Active Bounty Scan Results\n\n**Scan Time:** {bounty_list[0]['Scan Time']}\n\n"
    for idx, item in enumerate(bounty_list, start=1):
        title = item.get('title', '')
        repo = item.get('Repository', '')
        comments = item.get('Comments', '')
        last_updated = item.get('Last Updated', '')
        formatted += f"#### {idx}. [{title}]({repo})\n"
        formatted += f"- **Repository:** [{repo}](https://github.com/{repo.split('/')[-1]})\n"
        formatted += f"- **Comments:** {comments}\n"
        formatted += f"- **Last Updated:** {last_updated}\n\n"
    formatted += f"**Summary:** 🎯 Bounty Alert: {len(bounty_list)} New Opportunityies found."
    return formatted
```