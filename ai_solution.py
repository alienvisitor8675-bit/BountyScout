```python
import re

def extract_bounty_info(input_str):
    pattern = r'^\d+\.\s\[\s*(.*?)\]\s\((.*?)\)\s-\s**Repository:**\s\[(.*?)\]\s\((.*?)\)\s-\s**Comments:**\s(\d+)\s-\s**Last Updated:**\s(.*?)(\s|$)'
    matches = re.finditer(pattern, input_str, re.MULTILINE)
    result = []
    for match in matches:
        issue_link = match.group(2)
        repository = match.group(3)
        comments = match.group(5)
        last_updated = match.group(6)
        result.append({
            "repository": repository,
            "comments": comments,
            "last_updated": last_updated,
            "issue_link": issue_link
        })
    return result
```