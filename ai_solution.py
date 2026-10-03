```python
import re

def get_new_opportunities(text):
    """
    Extracts the number of new opportunities from a given text string.
    
    Args:
        text (str): The input text string containing the number of opportunities.
        
    Returns:
        int: The number of new opportunities found.
        
    Example:
        Input: "10 New Opportunityies found"
        Output: 10
        
        Input: "11 New Opportunities found"
        Output: 11
    """
    match = re.match(r'^\D*(\d+).*', text)
    return int(match.group(1)) if match else 0

# Example usage:
issue_text = "10 New Opportunityies found"
print(get_new_opportunities(issue_text))  # Output: 10

issue_text = "11 New Opportunities found"
print(get_new_opportunities(issue_text))  # Output: 11
```