```python
import re

def extract_github_details(text):
    pattern = r'#### (\d+). (.+?)\n- **Repository:** (.+?)\n- **Last Updated:** (.+?)\n'
    matches = re.findall(pattern, text, re.DOTALL)
    return [
        {
            "number": f"GitHub Issue #{match[0]}",
            "title": match[1],
            "repository": match[2],
            "last_updated": match[3]
        }
        for match in matches
    ]

# Example usage:
text = """
#### 1. [Bug: withdraw_all bypasses the documented minimum holding period](https://github.com/Neurowealth/NeuroWealth-Smartcontract/issues/894)
- **Repository:** [Neurowealth/NeuroWealth-Smartcontract](https://github.com/Neurowealth/NeuroWealth-Smartcontract)
- **Comments:** 3
- **Last Updated:** 2026-09-30T14:50:57Z

#### 2. [🎯 Micro Bounty Alert: 3 New Opportunities](https://github.com/2510034127qq-wq/BountyScout/issues/200)
- **Repository:** [2510034127qq-wq/BountyScout](https://github.com/2510034127qq-wq/BountyScout)
- **Comments:** 0
- **Last Updated:** 2026-09-30T14:42:23Z
"""

result = extract_github_details(text)
print(result)
```