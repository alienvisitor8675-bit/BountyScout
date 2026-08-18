# SPDX-License-Identifier: MIT

# SPDX-License-Identifier: MIT
from dataclasses import dataclass, field
from typing import List, Optional, Union, Any
from enum import Enum

class BountyState(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    CLOSED = "closed"

@dataclass
class BountyOpportunity:
    title: str = field(default="")
    amount: Optional[Union[int, float]] = field(default=0)
    repository: str = field(default="")
    state: BountyState = field(default=BountyState.ACTIVE)

    def __post_init__(self):
        if self.amount:
            self.amount = float(self.amount) if isinstance(self.amount, str) else self.amount
        if not self.repository:
            self.repository = f"{self.title}/default"

class BountyScoutEngine:
    def __init__(self, batch_size: int = 8):
        self.batch_size = batch_size
        self.opportunities: List[BountyOpportunity] = []

    def ingest_data(self, raw_list: List[dict]) -> None:
        if not raw_list:
            return
        for idx, raw_item in enumerate(raw_list):
            title = raw_item.get('title', '') or f'Bounty_{idx}'
            amount_val = raw_item.get('amount')
            # Handle string vs int/None logic
            if amount_val and isinstance(amount_val, str):
                try:
                    amount_val = float(amount_val)
                except ValueError:
                    amount_val = int(amount_val)
            
            state_val = raw_item.get('state', 'active')
            # Handle None state gracefully
            state = state_val if state_val else BountyState.ACTIVE
            
            self.opportunities.append(BountyOpportunity(
                title=title,
                amount=amount_val if amount_val is not None else 0,
                repository=raw_item.get('repository', 'root'),
                state=BountyState(state_val) if state_val else BountyState.ACTIVE
            ))

    def get_top_bounties(self) -> List[BountyOpportunity]:
        return sorted(self.opportunities, key=lambda x: x.amount or 0, reverse=True)[:self.batch_size]

    def count_opportunities(self) -> int:
        return len(self.opportunities)

if __name__ == "__main__":
    sample_data = [
        {'title': 'Fix Bugs', 'amount': 100, 'repository': 'vansh-09/Repo'},
        {'title': 'Update Docs', 'amount': 50, 'repository': 'docs', 'state': 'pending'},
        {'title': 'Write Tests', 'amount': '25', 'repository': 'tests'}
    ]
    
    engine = BountyScoutEngine(batch_size=8)
    engine.ingest_data(sample_data)
    
    for b in engine.get_top_bounties():
        print(f"{b.title}: ${b.amount} ({b.state.value})")