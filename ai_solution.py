```python
# Define merchant tiers and corresponding percentages for rolling reserve
merchant_tiers = {
    1: 0.015,  # 1.5%
    2: 0.02,    # 2%
    3: 0.025,  # 2.5%
    4: 0.03     # 3%
}

# Define the holding periods in days based on tiers
holding_periods = {
    1: 7,
    2: 14,
    3: 21,
    4: 28
}

def calculate_rolling_reserve(total_amount, tier):
    """
    Calculate the rolling reserve based on the merchant's tier.
    """
    return total_amount * merchant_tiers.get(tier, 0.015)

def determine_settlement_holding_period(tier):
    """
    Determine the settlement holding period based on the merchant's tier.
    """
    return holding_periods.get(tier, 7)

# Example usage
total_amount = 100000  # Example amount
tier = 3

rolling_reserve = calculate_rolling_reserve(total_amount, tier)
holding_days = determine_settlement_holding_period(tier)

print(f"Total Amount: ${total_amount:.2f}")
print(f"Merchant Tier {tier}: {merchant_tiers[tier]*100}%")
print(f"Rolling Reserve: ${rolling_reserve:.2f}")
print(f"Settlement Holding Period: {holding_days} days")
```