```python
class BountyScout:
    """BountyScout class for summarizing bounties."""
    
    def summarize_bounties(self, bounty_data):
        """Summarize bounties in a formatted Markdown string.
        
        Example usage:
        ```python
        bounty_data = [
            {
                "Repository": "[terminator2-agent/terminator2-agent.github.io](https://github.com/terminator2-agent/terminator2-agent.github.io)",
                "Economic status": "VERIFY",
                "Payment signals": "bounty, paid, reward, usd, usdc"
            },
            {
                "Repository": "[zkp2p/peer-link](https://github.com/zkp2p/peer-link)",
                "Economic status": "VERIFY",
                "Payment signals": "$, bounty, paid, payment, usd, usdc"
            },
            # Add more items as needed
        ]
        summary = BountyScout().summarize_bounties(bounty_data)
        print(summary)
        """
        summary = "### Bounty Summary\n\n"
        for item in bounty_data:
            repository = item.get("Repository", "")
            economic_status = item.get("Economic status", "")
            payment_signals = item.get("Payment signals", "")
            summary += f"- **Repository**: {repository}\n"
            summary += f"  **Economic status**: {economic_status}\n"
            summary += f"  **Payment signals**: {payment_signals}\n"
        return summary
```