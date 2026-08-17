class BountyScout:
    def __init__(self, api_url: str = "https://api.example.com/bounty"):
        self.api_url = api_url
        self.cache = {}
        self.poll_interval = 30
        self.running = False

    async def fetch_opportunities(self) -> list[dict]:
        try:
            # Simulate async API fetch
            response = await self._make_request()
            data = response.get('opportunities', [])
            self.cache['last_fetched'] = time.time()
            return data
        except Exception as e:
            print(f"Fetch error: {e}")
            return []

    async def _make_request(self) -> dict:
        if self.api_url:
            return await asyncio.get_event_loop().run_in_executor(
                None, lambda: requests.get(self.api_url)
            )
        return {}

    async def filter_new_opportunities(self, existing_ids: set[str] = None) -> list[dict]:
        if existing_ids is None:
            existing_ids = set()
        opportunities = await self.fetch_opportunities()
        new = [op for op in opportunities if op.get('id') not in existing_ids]
        new_ids = {op.get('id') for op in new}
        existing_ids.update(new_ids)
        return new

    async def process_opportunities(self, new_ops: list[dict]) -> int:
        success = 0
        for op in new_ops:
            try:
                # Notify handler
                await self._notify(op)
                success += 1
            except Exception as e:
                print(f"Process error for {op.get('id')}: {e}")
        return success

    async def _notify(self, op: dict) -> None:
        channel = op.get('channel', 'bounty_channel')
        message = f"🎯 {op.get('title')} - {op.get('reward', 'N/A')}"
        await self._publish(channel, message)

    async def _publish(self, channel: str, message: str) -> None:
        print(f"[{channel}] {message}")

    def run(self, count: int = 6) -> None:
        self.running = True
        initial_ids: set[str] = set()

        async def loop():
            while self.running:
                try:
                    new_ops = await self.filter_new_opportunities(initial_ids)
                    if new_ops:
                        await self.process_opportunities(new_ops)
                        initial_ids.update(op['id'] for op in new_ops)
                except Exception as e:
                    print(f"Loop error: {e}")
                await asyncio.sleep(self.poll_interval)

        asyncio.run(loop())


class Opportunity:
    def __init__(self, id: str, title: str, reward: str, channel: str = "bounty_channel"):
        self.id = id
        self.title = title
        self.reward = reward
        self.channel = channel
        self.processed = False

    def __repr__(self):
        return f"Opportunity(id={self.id}, title={self.title}, reward={self.reward})"


class BountyScoutManager:
    def __init__(self, scout: BountyScout, name: str = "MainBountyScout"):
        self.scout = scout
        self.name = name
        self.metrics = {"total_fetched": 0, "new_processed": 0}

    async def orchestrate(self) -> None:
        async def fetch_and_filter():
            raw = await self.scout.fetch_opportunities()
            self.metrics["total_fetched"] += len(raw)
            for op in raw:
                if 'id' in op:
                    op['processed'] = False
            return raw

        new_ops = await fetch_and_filter()
        if new_ops:
            self.scout.metrics["new_processed"] += len(new_ops)
            for op in new_ops:
                await self.scout._notify(op)
                op['processed'] = True


if __name__ == "__main__":
    scout = BountyScout()
    manager = BountyScoutManager(scout, "MainBountyScout")
    scout.poll_interval = 30
    scout.running = True
    asyncio.run(scout.run(count=6))