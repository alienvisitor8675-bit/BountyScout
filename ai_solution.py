```python
def handle_issues():
    issue = cloudflare_cloudflared_issue
    if issue:
        if issue.repo == "cloudflare/cloudflared" and issue.number == 1617:
            return {
                "checksum": "b3b18d98a08c48d347c5b5e89679f975",
                "artifact": "checksums.txt"
            }
    issue = makazhanalpamys_soup_issue
    if issue:
        if issue.repo == "MakazhanAlpamys/Soup" and issue.number == 1530:
            data = issue.data
            if data:
                return data
    return None
```