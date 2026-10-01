To solve this problem, we need to extract the repository name, issue number, and issue title from a list of items presented in a specific format. Each item begins with a number, followed by the repository name, an issue number in parentheses, and the issue title.

### Approach
1. **Problem Analysis**: The task is to extract three pieces of information from each line: the repository name, the issue number, and the issue title. Each line starts with a number, followed by the repository name, an issue number in parentheses, and the title, which may include additional details.
2. **Intuition**: Using regular expressions is an efficient way to extract structured information from text. We can apply a regex pattern to each line to capture the required components.
3. **Algorithm Selection**: We will use a regular expression to match the components. The regex will identify the repository, issue number, and title from each line.
4. **Complexity Analysis**: The solution efficiently processes each line with a single regex match, resulting in a linear time complexity relative to the number of lines.

### Solution Code
```python
import re

pattern = r'^\d+\.\s+([^\(]+?)\s+\((\d+)\)\s+\((.*)\)'
results = []

with open('input.txt', 'r') as file:
    for line in file:
        line = line.strip()
        match = re.match(pattern, line)
        if match:
            repo = match.group(1)
            issue_number = match.group(2)
            title = match.group(3)
            results.append((repo, issue_number, title))

for repo, issue, title in results:
    print(f"Repository: {repo}, Issue #{issue}: {title}")
```

### Explanation
- **Pattern Matching**: The regex `r'^\d+\.\s+([^\(]+?)\s+\((\d+)\)\s+\((.*)\)'` is used to capture the repository, issue number, and title from each line.
- **Loop Through Lines**: Each line from the input file is processed to extract the components using the regex.
- **Result Processing**: The extracted components are stored in a list and then printed in a formatted manner.

This approach efficiently extracts the required information using regular expressions, ensuring clarity and correctness in the output.