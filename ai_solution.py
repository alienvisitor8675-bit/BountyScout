```python
import re

def format_github_issues(issues):
    formatted = []
    for issue in issues:
        lines = issue.split('\n')
        first_line = lines[0].strip()
        match = re.match(r'^(\d+)\.\s*\[\[(.*)\]\]\((.*)\)', first_line)
        if match:
            num = match.group(1)
            title = match.group(2)
            url = match.group(3)
        else:
            num, title, url = '', '', ''
        
        repo_line = lines[1].strip()
        match_repo = re.match(r'\*\*Repository:\*\* \[([^\[\]]*)\]', repo_line)
        if match_repo:
            repo = match_repo.group(1)
        else:
            repo = ''
        
        comments = lines[2].strip().split(': ')[1]
        last_updated = lines[3].strip().split(': ')[1]
        
        formatted_issue = f"- **{num}** [{title}]({url})"
        formatted_issue += f"\n  - **Repository:** {repo}"
        formatted_issue += f"\n  - **Comments:** {comments}"
        formatted_issue += f"\n  - **Last Updated:** {last_updated}"
        formatted.append(formatted_issue)
    
    return '\n'.join(formatted)
```