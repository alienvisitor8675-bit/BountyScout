```python
def process_bounties(bounties):
    formatted_bounties = []
    for bounty in bounties:
        formatted_bounties.append(f"- **{bounty['title']}**\n- **Repository:** [{bounty['repository']}]({bounty['url']})\n- **Comments:** {bounty['comments']}\n- **Last Updated:** {bounty['last_updated']}\n\n")
    return "".join(formatted_bounties)
```