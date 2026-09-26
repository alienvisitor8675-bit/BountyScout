```python
def format_bounties(bounty_list):
    formatted_bounties = []
    for issue in bounty_list:
        title = issue['title']
        repository = f"**Repository:** [{issue['repository']}](https://github.com/{issue['repository_url']})"
        comments = f"**Comments:** {issue['comments']}"
        last_updated = f"**Last Updated:** {issue['last_updated']}"
        formatted_line = f"#### {issue['number']}. {title}\n- {repository}\n- {comments}\n- {last_updated}\n"
        formatted_bounties.append(formatted_line)
    return "\n".join(formatted_bounties)

# Example usage:
bounty_list = [
    {
        'number': '1',
        'title': '[security: remove dangerouslySetInnerHTML from the root layout]',
        'repository': '[C-Address-Onboarding-Bridge/C-Address-Onboarding-Bridge--Frontend-](https://github.com/C-Address-Onboarding-Bridge/C-Address-Onboarding-Bridge--Frontend-)',
        'comments': '3',
        'last_updated': '2026-09-26T09:03:49Z'
    },
    # Add more items as needed
]

# The function will format each item accordingly.
```