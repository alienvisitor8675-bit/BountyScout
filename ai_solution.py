```python
def format_bounties(bounty_list):
    formatted_bounties = []
    for item in bounty_list:
        formatted_bounties.append({
            "Number": item["Number"],
            "Title": item["Title"],
            "Repository": item["Repository"],
            "Comments": item["Comments"],
            "Last Updated": item["Last Updated"]
        })
    return formatted_bounties

# Example usage:
bounties = [
    {"Number": "1.", "Title": "[Bounty 3: tests-mode, paid without a merge]", "Repository": "[drexthealpha/knos-e2e](https://github.com/drexthealpha/knos-e2e)", "Comments": "0", "Last Updated": "2026-10-02T09:19:57Z"},
    # ... other items ...
]

result = format_bounties(bounties)
for bounty in result:
    print(bounty)
```