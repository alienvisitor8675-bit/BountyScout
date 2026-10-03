```python
def format_bounties(bounties):
    count = len(bounties)
    repo_names = [b['Repository'] for b in bounties]
    return f" gündem 🎯 Bounty Alert: {count} New Opportunityies found\n\n{'\n'.join([f'#### {name}' for name in repo_names])}."
```