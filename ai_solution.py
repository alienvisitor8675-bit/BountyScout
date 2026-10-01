To solve this problem, we need to create a function that processes a list of bounties and formats them into a specific string format. Each bounty should be formatted as a bullet point with the number, title, repository, and last updated date.

### Approach
1. **Problem Analysis**: We need to extract specific details from each item in the list and format them into a bullet point string.
2. **Extracting Information**: For each item, we extract the number, title, repository, and last updated date.
3. **Formatting**: Each extracted information is formatted into a string with the specified structure.
4. **Combining Results**: All formatted strings are combined into a single string with each bullet point on a new line.

### Solution Code
```python
def format_bounties(bounty_list):
    formatted = []
    for item in bounty_list:
        number = item['number']
        title = item['title']
        repository = item['repository']
        last_updated = item['last_updated']
        formatted.append(f"Bounty {number}. \"{title}\". Repository: [{repository}]. Last updated: {last_updated}.")
    return '\n'.join(formatted)
```

### Explanation
The function `format_bounties` takes a list of bounty items as input. It iterates over each item, extracts the relevant details, and formats them into a bullet point string. Each bullet point starts with "Bounty" followed by the number, the title in quotes, the repository in brackets, and the last updated date in parentheses. The formatted strings are then joined into a single string with each bullet point on a new line, providing a clear and structured output of the bounties.