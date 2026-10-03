```python
def process_bounty_scan(scan_results):
    processed = []
    for item in scan_results:
        processed_item = {
            "title": item["title"],
            "repository": item["repository"],
            "comments": item["comments"],
            "last_updated": item["last_updated"]
        }
        processed.append(processed_item)
    return processed
```