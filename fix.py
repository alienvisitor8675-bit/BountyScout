# SPDX-License-Identifier: MIT

# SPDX-License-Identifier: MIT
from dataclasses import dataclass, field
from typing import List, Union, Optional, Any, Dict
from enum import Enum

class Status(Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    PENDING = "pending"

@dataclass
class Opportunity:
    id: Union[int, str]
    title: str
    reward: float
    tags: List[str] = field(default_factory=list)
    status: Status = Status.ACTIVE

class BountyScout:
    def __init__(self, source: str = "bounties"):
        self.source = source
        self._buffer: List[Opportunity] = []

    def load_feed(self, raw_items: List[Dict[str, Any]]) -> List[Opportunity]:
        opportunities = []
        for idx, item in enumerate(raw_items):
            # Resolve title to default if missing or None
            title = item.get('title', f'Bounty-{idx}')
            
            # Normalize reward to float
            raw_reward = item.get('reward', 0.0)
            if isinstance(raw_reward, str):
                raw_reward = float(raw_reward)

            # Resolve tags to list if needed (handles "single-string-tag")
            raw_tags = item.get('tags', [])
            if isinstance(raw_tags, str):
                raw_tags = [raw_tags]

            # Map status string to Enum safely
            raw_status = item.get('status', 'active')
            if raw_status is None:
                raw_status = Status.ACTIVE

            opportunities.append(
                Opportunity(
                    id=item.get('id', idx),
                    title=title,
                    reward=raw_reward,
                    tags=raw_tags,
                    status=raw_status
                )
            )
        return opportunities

    def find_highest_payer(self) -> Optional[Opportunity]:
        if not self._buffer:
            return None
        return max(self._buffer, key=lambda x: x.reward)

    def filter_by_tags(self, tag: str) -> List[Opportunity]:
        return [op for op in self._buffer if tag in op.tags]