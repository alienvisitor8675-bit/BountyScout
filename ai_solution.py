```python
def summarize_bounties(bounty_data):
    summary = "Bounty Summary:\n"
    for item in bounty_data:
        repository = item.get("Repository", "")
        economic_status = item.get("Economic status", "")
        payment_signals = item.get("Payment signals", "")
        summary += f"- Repository: {repository}\n"
        summary += f"  Economic status: {economic_status}\n"
        summary += f"  Payment signals: {payment_signals}\n"
    return summary

# Example usage:
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

result = summarize_bounties(bounty_data)
print(result)
```