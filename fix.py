```python
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import json
import sys

@dataclass
class BountyOpportunity:
    title: str
    reward: int
    platform: str
    url: str
    difficulty: str
    deadline: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        result = {
            'title': self.title,
            'reward': self.reward,
            'platform': self.platform,
            'url': self.url,
            'difficulty': self.difficulty,
            'deadline': self.deadline,
            'tags': self.tags,
            'created_at': self.created_at.isoformat()
        }
        if result['deadline']:
            result['deadline'] = self.deadline
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class BountyScout:
    def __init__(self):
        self.opportunities: List[BountyOpportunity] = []
        self.source: Optional[str] = None
    
    def add_opportunity(self, 
                       title: str, 
                       reward: int, 
                       platform: str, 
                       url: str,
                       difficulty: str = 'Medium',
                       deadline: Optional[str] = None,
                       tags: Optional[List[str]] = None) -> BountyOpportunity:
        bounty = BountyOpportunity(
            title=title,
            reward=reward,
            platform=platform,
            url=url,
            difficulty=difficulty,
            deadline=deadline or datetime.now().strftime('%Y-%m-%d'),
            tags=tags or []
        )
        self.opportunities.append(bounty)
        return bounty
    
    def load_opportunities(self, data: List[BountyOpportunity]) -> 'BountyScout':
        self.opportunities.extend(data)
        return self
    
    def filter_by_difficulty(self, difficulty: str) -> List[BountyOpportunity]:
        return [op for op in self.opportunities if op.difficulty == difficulty]
    
    def filter_by_platform(self, platform: str) -> List[BountyOpportunity]:
        return [op for op in self.opportunities if op.platform == platform]
    
    def filter_by_reward_range(self, min_reward: int, max_reward: int) -> List[BountyOpportunity]:
        return [op for op in self.opportunities if min_reward <= op.reward <= max_reward]
    
    def get_total_reward(self) -> int:
        return sum(op.reward for op in self.opportunities)
    
    def get_high_value_opportunities(self, threshold: int = 500) -> List[BountyOpportunity]:
        return [op for op in self.opportunities if op.reward >= threshold]
    
    def sort_by_reward_desc(self) -> 'BountyScout':
        self.opportunities.sort(key=lambda x: x.reward, reverse=True)
        return self
    
    def sort_by_deadline_asc(self) -> 'BountyScout':
        self.opportunities.sort(key=lambda x: x.deadline)
        return self
    
    def export_to_json(self, filepath: str) -> str:
        return self.opportunities[0].to_json() if len(self.opportunities) == 1 else json.dumps(
            [op.to_dict() for op in self.opportunities], indent=2
        )
    
    def print_report(self) -> None:
        print(f"\n{'='*60}")
        print(f"🎯 BOUNTY REPORT - {len(self.opportunities)} New Opportunity{'ies' if len(self.opportunities) > 1 else ''}")
        print(f"{'='*60}\n")
        
        for i, bounty in enumerate(self.opportunities, 1):
            print(f"{i}. [{bounty.platform}] {bounty.title}")
            print(f"   💰 Reward: ${bounty.reward:,}")
            print(f"   🏷️  Difficulty: {bounty.difficulty}")
            print(f"   🔗 Link: {bounty.url}")
            if bounty.deadline:
                print(f"   ⏰ Deadline: {bounty.deadline}")
            if bounty.tags:
                print(f"   📚 Tags: {', '.join(bounty.tags)}")
            print()
        
        print(f"{'='*60}\n")
    
    def export_all(self, filepath: str = 'bounties.json') -> str:
        data = self.export_to_json(filepath)
        with open(filepath, 'w') as f:
            f.write(data)
        return data


def parse_opportunities(input_data: dict) -> List[BountyOpportunity]:
    def get_value(key: str, default=None):
        return input_data.get(key, default)
    
    def get_int(key: str, default=0):
        val = get_value(key, default)
        return int(val) if isinstance(val, str) else val
    
    def get_str(key: str, default=''):
        val = get_value(key, default)
        return str(val) if val else default
    
    bounty_list = []
    
    if 'opportunities' in input_data:
        opportunities = input_data['opportunities']
        for item in opportunities:
            bounty = BountyOpportunity(
                title=get_str('title', item.get('title', 'New Opportunity')),
                reward=get_int('reward', item.get('reward', 100)),
                platform=get_str('platform', item.get('platform', 'Unknown')),
                url=get_str('url', item.get('url', '#')),
                difficulty=get_str('difficulty', item.get('difficulty', 'Medium')),
                deadline=get_str('deadline', item.get('deadline')),
                tags=item.get('tags', [])
            )
            bounty_list.append(bounty)
    
    return bounty_list


def main():
    scout = BountyScout()
    
    # Simulating input data from GitHub issue
    sample_data = {
        'opportunities': [
            {'title': 'Vulnerability Hunter', 'reward': 1500, 'platform': 'HackerOne', 'url': '#1', 'difficulty': 'Hard'},
            {'title': 'Bug Bash Sprint', 'reward': 750, 'platform': 'TugBoat', 'url': '#2', 'difficulty': 'Medium'},
            {'title': 'Security Audit', 'reward': 3000, 'platform': 'Bugcrowd', 'url': '#3', 'difficulty': 'Expert'},
            {'title': 'Smart Contract Fix', 'reward': 1200, 'platform': 'Immunefi', 'url': '#4', 'difficulty': 'Hard'},
            {'title': 'API Endpoint Test', 'reward': 450, 'platform': 'Pwned', 'url': '#5', 'difficulty': 'Easy'}
        ]
    }
    
    # Parse and load opportunities
    bounties = parse_opportunities(sample_data)
    scout.load_opportunities(bounties)
    
    # Print the report
    scout.print_report()
    
    # Export to JSON
    scout.export_all('bounty_scout.json')
    
    # Sort by reward
    scout.sort_by_reward_desc()
    
    # Print high-value opportunities
    print("🔥 High Value Picks ($1000+)")
    for bounty in scout.filter_by_reward_range(1000, 5000):
        print(f"   - {bounty.title}: ${bounty.reward}")
    
    print("\n✅ Bounty Scouting Complete!")


if __name__ == '__main__':
    main()
```