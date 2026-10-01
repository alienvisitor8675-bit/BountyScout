To solve this task, we need to structure the given list of issues into a JSON format with specific keys. The goal is to present the information in a clear and organized manner.

### Approach
The approach involves creating a function that processes the given list of issues and converts them into a JSON structure. Each issue is converted into a dictionary with specific keys: `id`, `title`, `repository`, `comments`, `last_updated`, and `url`. The function then returns this JSON structure.

### Solution Code
```python
import json

def format_issues(issues):
    items = []
    for idx, issue in enumerate(issues, 1):
        items.append({
            "id": str(idx),
            "title": issue["title"],
            "repository": issue["Repository"],
            "comments": issue["Comments"],
            "last_updated": issue["Last Updated"],
            "url": issue["url"]
        })
    return json.dumps({"items": items}, indent=2)

# Example input data
issues = [
    {
        "title": "Bounty Hunter: kills by party bots don't count",
        "Repository": "MondoTruth/standart-npc",
        "Comments": "0",
        "Last Updated": "2026-10-01T18:00:30Z",
        "url": "https://github.com/MondoTruth/standart-npc/issues/7"
    },
    {
        "title": "Epic: Phase 2: platformer courses, control, skills, health, progression, voice, and a clearer game",
        "Repository": "rumcan/Heavy-Metal-GP",
        "Comments": "0",
        "Last Updated": "2026-10-01T17:49:12Z",
        "url": "https://github.com/rumcan/Heavy-Metal-GP/issues/106"
    },
    {
        "title": "[Bounty proposal] feat(python-cli): conversations -> Jupyter notebook (.ipynb) export recipe ($25 proposed)",
        "Repository": "BasedHardware/omi",
        "Comments": "0",
        "Last Updated": "2026-10-01T17:46:09Z",
        "url": "https://github.com/BasedHardware/omi/issues/20193"
    },
    {
        "title": "Add funding model comparison table to docs/drips-wave-points.md",
        "Repository": "opensource-maintainer-toolkit/open-source-maintainer-toolkit",
        "Comments": "1",
        "Last Updated": "2026-10-01T17:43:48Z",
        "url": "https://github.com/opensource-maintainer-toolkit/open-source-maintainer-toolkit/issues/43"
    },
    {
        "title": "[Rubick] Comprehensive list of every ability steal with broken ability links",
        "Repository": "ValveSoftware/Dota2-Gameplay",
        "Comments": "0",
        "Last Updated": "2026-10-01T17:32:44Z",
        "url": "https://github.com/ValveSoftware/Dota2-Gameplay/issues/34268"
    },
    {
        "title": "WEB-UX-02 — Cockpit opérateur plus lisible, pédagogique et visuellement hiérarchisé",
        "Repository": "3a7i3/crypto-ia-terminal",
        "Comments": "4",
        "Last Updated": "2026-10-01T17:23:52Z",
        "url": "https://github.com/3a7i3/crypto-ia-terminal/issues/283"
    },
    {
        "title": "fix(mcp): ChatGPT directory listing grants memories.read on",
        "Repository": "ValveSoftware/Dota2-Gameplay",
        "Comments": "0",
        "Last Updated": "2026-10-01T17:32:44Z",
        "url": "https://github.com/ValveSoftware/Dota2-Gameplay/issues/34268"
    }
]

# The function will return the formatted JSON
print(format_issues(issues))
```

### Explanation
The function `format_issues` takes a list of issues as input and processes each issue to create a structured JSON output. Each issue is converted into a dictionary with the required keys, and the list of these dictionaries is returned as a JSON object. This makes the information easy to read and organized.