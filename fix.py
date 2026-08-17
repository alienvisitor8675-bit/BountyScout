```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Callable, Dict, Any, Union
from queue import Queue
import threading
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Status(Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    PENDING = "PENDING"


@dataclass
class Bounty:
    id: str
    title: str
    platform: str
    reward: int
    currency: str
    status: Status
    deadline: Optional[datetime]
    description: str
    tags: List[str]
    url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'platform': self.platform,
            'reward': self.reward,
            'currency': self.currency,
            'status': self.status.value,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'description': self.description,
            'tags': self.tags,
            'url': self.url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class BountySquad:
    def __init__(self, name: str, default_interval: int = 60):
        self.name = name
        self.interval = default_interval
        self._bounties: Dict[str, Bounty] = {}
        self._queue: Queue[Bounty] = Queue()
        self._active: threading.Thread = None
        self._running: threading.Event = threading.Event()
        self._callbacks: Dict[str, List[Callable]] = {
            'on_new': [],
            'on_status_change': [],
            'on_expired': []
        }
        self._last_check: Dict[str, datetime] = {}
        self._stale_threshold: timedelta = timedelta(minutes=30)

    def add_bounty(self, bounty: Bounty):
        if bounty.id in self._bounties:
            logger.info(f"Bounty {bounty.id} already exists, updating...")
        self._bounties[bounty.id] = bounty
        self._queue.put(bounty)
        self._trigger_event('on_new', bounty)

    def get_bounty(self, bounty_id: str) -> Optional[Bounty]:
        return self._bounties.get(bounty_id)

    def get_active_bounties(self) -> List[Bounty]:
        now = datetime.now()
        return [
            b for b in self._bounties.values()
            if b.status == Status.ACTIVE
            and (b.deadline is None or b.deadline > now)
        ]

    def _trigger_event(self, event_type: str, bounty: Bounty):
        callbacks = self._callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                callback(bounty)
            except Exception as e:
                logger.warning(f"Callback {event_type} failed: {e}")

    def register_callback(self, event: str, callback: Callable[[Bounty], None]):
        self._callbacks.setdefault(event, []).append(callback)

    def _process_queue(self):
        while self._running.is_set():
            try:
                bounty = self._queue.get(timeout=self.interval / 1000)
                self._trigger_event('on_queue', bounty)
                self._queue.task_done()
            except Exception as e:
                logger.debug(f"Queue processing error: {e}")

    def _check_deadlines(self):
        now = datetime.now()
        stale_threshold = self._stale_threshold
        for bounty in self._bounties.values():
            if bounty.deadline and bounty.deadline < now:
                if bounty.status != Status.RESOLVED:
                    bounty.status = Status.PENDING
                    self._trigger_event('on_status_change', bounty)
                else:
                    self._queue.put(bounty)
            else:
                self._last_check[bounty.id] = now

    def run(self):
        self._active = threading.Thread(target=self._process_queue, name=f"{self.name}-Worker")
        self._active.start()
        logger.info(f"Squad {self.name} started")

    def stop(self):
        self._running.set()
        if self._active:
            self._active.join()
        logger.info(f"Squad {self.name} stopped")


class BountyAlert:
    def __init__(self, squad: BountySquad, threshold: int = 5):
        self.squad = squad
        self.threshold = threshold
        self._bounties_alerted: Dict[str, List[datetime]] = {}
        self._cooldown: timedelta = timedelta(minutes=5)

    def _check_threshold(self, bounty: Bounty):
        key = f"{bounty.platform}:{bounty.title}"
        last_alert = self._bounties_alerted.get(key, [None])
        if last_alert and (datetime.now() - last_alert[0]) < self._cooldown:
            return

        if len(last_alert) < self.threshold:
            self._bounties_alerted[key] = last_alert + [datetime.now()]
            logger.info(f"🎯 Alert: {bounty.title} - {bounty.platform}")

    def listen(self, callback: Callable[[Bounty], None]):
        def wrapped(bounty: Bounty):
            self._check_threshold(bounty)
            callback(bounty)
        self.squad.register_callback('on_new', wrapped)

    def notify(self, key: str, value: Any):
        self._bounties_alerted[key] = self._bounties_alerted.get(key, []) + [value]


def create_bounty(title: str, platform: str = 'DeFiLlama', reward: int = 150,
                  currency: str = 'USDC', tags: List[str] = ['DeFi', 'Smart Contract'],
                  url: str = '', deadline: Optional[datetime] = None,
                  status: Status = Status.ACTIVE) -> Bounty:
    return Bounty(
        id=f"{platform.lower()}:{title.replace(' ', '')}",
        title=title,
        platform=platform,
        reward=reward,
        currency=currency,
        tags=tags,
        url=url,
        deadline=deadline,
        status=status
    )


class NotificationHub:
    def __init__(self, channels: List[str] = None):
        self.channels = channels or ['console']
        self._callbacks: Dict[str, List[Callable]] = {channel: [] for channel in channels}

    def subscribe(self, channel: str, callback: Callable[[Bounty], None]):
        if channel in self._callbacks:
            self._callbacks[channel].append(callback)
            logger.info(f"Subscribed to {channel} with {len(self._callbacks[channel])} callbacks")
        else:
            self._callbacks[channel] = [callback]

    def _notify(self, channel: str, bounty: Bounty):
        for callback in self._callbacks.get(channel, []):
            try:
                callback(bounty)
            except Exception as e:
                logger.debug(f"Notification error on {channel}: {e}")

    def broadcast(self, bounty: Bounty):
        for channel in self.channels:
            self._notify(channel, bounty)


def run_bounty_workflow():
    squad = BountySquad(name='AlphaSquad')
    alert = BountyAlert(squad, threshold=5)
    hub = NotificationHub(channels=['console', 'discord'])

    hub.subscribe('console', lambda b: logger.info(f"✅ New Bounty: {b.title} - Reward: {b.reward}{b.currency}"))
    hub.subscribe('discord', lambda b: print(f"🚀 Discord: [{b.platform}] {b.title} - ${b.reward}"))

    @squad.register_callback('on_new')
    def handle_new(bounty: Bounty):
        logger.info(f"📢 New bounty detected: {bounty.id}")
        hub.broadcast(bounty)
        squad.add_bounty(bounty)

    @squad.register_callback('on_status_change')
    def handle_change(bounty: Bounty):
        logger.info(f"🔄 Status updated: {bounty.id} -> {bounty.status.value}")

    def main():
        squad.add_bounty(create_bounty(
            title='Ethereum NFT Staking',
            platform='Ethereum',
            reward=250,
            currency='ETH',
            tags=['NFT', 'Staking'],
            url='https://opensea.io',
            deadline=datetime.now() + timedelta(days=7)
        ))

        def process_loop():
            while squad.get_bounty('ethnft'):
                time.sleep(5)

        run_bounty_workflow()
        logger.info("Bounty workflow running...")

    if __name__ == "__main__":
        from time import time
        thread = threading.Thread(target=process_loop, name="ProcessLoop")
        thread.daemon = True
        thread.start()

        for _ in range(3):
            main()
            time.sleep(8)
            thread.join(timeout=5)

        logger.info("Bounty workflow complete.")
```