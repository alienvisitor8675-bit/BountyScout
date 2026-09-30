```python
def discover_agents(self):
    agents = self.agents.all()
    return sorted(agents, key=lambda x: x.type)
```