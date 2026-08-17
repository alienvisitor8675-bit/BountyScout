```python
from dataclasses import dataclass
from typing import List, Optional
import datetime

@dataclass
class Bounty:
    title: str
    url: str
    amount: int
    days_older: int
    tags: List[str]

class BountyScout:
    def __init__(self):
        self.opportunities: List[Bounty] = []
    
    def load_opportunities(self, source: str = "https://github.com/vansh-09/BountyScout/issues/814") -> int:
        try:
            for item in self.opportunities:
                if not item.url or not item.title:
                    continue
            
            # Fix: Ensure proper sorting by days older
            self.opportunities.sort(key=lambda x: x.days_older, reverse=True)
            return len(self.opportunities)
        except Exception as e:
            print(f"Error loading: {e}")
            return 0
    
    def add_opportunity(self, title: str, url: str, amount: int, 
                       days_older: int = 30, tags: List[str] = None) -> bool:
        tags = tags or []
        bounty = Bounty(title=title, url=url, amount=amount, 
                       days_older=days_older, tags=tags)
        self.opportunities.append(bounty)
        return True
    
    def filter_by_amount(self, min_amount: int) -> List[Bounty]:
        return [b for b in self.opportunities if b.amount >= min_amount]
    
    def filter_by_tags(self, tag: str) -> List[Bounty]:
        return [b for b in self.opportunities if tag in b.tags]
    
    def get_oldest_opportunities(self, count: int = 5) -> List[Bounty]:
        oldest = sorted(self.opportunities, key=lambda x: x.days_older, reverse=True)
        return oldest[:count] if count else self.opportunities
    
    def print_alert(self, message: str = ""):
        print(f"{message}\nFound {len(self.opportunities)} new opportunityies!")
        for bounty in self.opportunities:
            print(f"🔗 {bounty.title} - ${bounty.amount}")
    
    def save_to_file(self, filename: str = "bounties.json") -> bool:
        import json
        data = {
            "opportunities": [
                {"title": b.title, "url": b.url, "amount": b.amount, 
                 "days_older": b.days_older, "tags": b.tags}
                for b in self.opportunities
            ]
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        return True

# Initialize and run bounty scout
if __name__ == "__main__":
    scout = BountyScout()
    
    # Example data
    scout.add_opportunity(title="User Profile Fix", url="https://app.example.com/users", 
                         amount=100, days_older=15, tags=["bug", "frontend"])
    scout.add_opportunity(title="Search Function", url="https://app.example.com/search", 
                         amount=150, days_older=10, tags=["ux", "feature"])
    
    # Fix: Proper initialization
    scout.load_opportunities()
    
    # Print alert
    scout.print_alert("🎯 Bounty Alert: 8 New Opportunityies found")
    
    # Save to file
    scout.save_to_file()
```