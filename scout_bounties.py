import json
import os
import urllib.request
import urllib.parse
import re
from datetime import datetime, timezone

# Configuration
STATE_FILE = "seen_bounties.json"
MAX_COMMENTS = 25  # Filter out overcrowded threads

# GitHub search queries for active bounty opportunities
SEARCH_QUERIES = [
    'is:issue is:open bounty in:title,body sort:updated-desc',
    'is:issue is:open reward bounty sort:updated-desc',
    'is:issue is:open "paid" "PR" "bounty" sort:updated-desc',
    'is:issue is:open "Opire" bounty sort:updated-desc',
]

def load_seen_bounties():
    """Load previously seen bounty URLs from the state file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
                elif isinstance(data, dict):
                    # Fallback if saved as an object (e.g., from older run)
                    return set(data.get("urls", [])) if data.get("urls") else set(data.keys())
                else:
                    # Handle edge cases
                    return set(data) if data else set()
        except Exception as e:
            print(f"Error loading state file: {e}")
            return set()
    return set()

def save_seen_bounties(seen_urls):
    """Save the updated list of seen bounty URLs."""
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_urls), f, indent=2)
    except Exception as e:
        print(f"Error saving state file: {e}")

def search_github(query, token=None):
    """Fetch search results from GitHub Issues API."""
    # Normalize query to avoid double encoding if needed, though query string handles it
    url = f"https://api.github.com/search/issues?{urllib.parse.urlencode({'q': query, 'per_page': 15})}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "MyPersonalBountyScout",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {}
        print(f"GitHub Search API HTTP Error for query '{query}': {e}")
        return {}
    except Exception as e:
        print(f"GitHub Search API Error for query '{query}': {e}")
        return {}

def is_clean_candidate(item):
    """Triage logic to filter out noisy, assigned, closed, or spam tasks."""
    # Ensure item is a dict/list structure
    if not isinstance(item, dict):
        return False
        
    # 1. Skip if already a Pull Request (nested object)
    if "pull_request" in item:
        return False
    
    # 2. Skip if already assigned
    if item.get("assignees"):
        return False
    
    # 3. Skip if thread is overcrowded (highly competitive)
    # Handle 'null' or '0' gracefully
    comments = int(item.get("comments", 0) or 0)
    if comments > MAX_COMMENTS:
        return False
        
    title = str(item.get("title", "")).lower()
    body = str(item.get("body", "")).lower()
    
    # 4. Skip cryptocurrency/article writing/spam keywords
    blocklist = [
        "airdrop", "referral", "casino", "gambling", "trading bot", 
        "blog post", "article writing", "tutorial proposal", "content creator"
    ]
    if any(term in title or term in body for term in blocklist):
        return False
        
    return True

def send_telegram_notification(token, chat_id, message):
    """Send a notification message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"Telegram notification sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")

def send_discord_notification(webhook_url, message):
    """Send a notification message via Discord Webhook."""
    payload = {
        "content": message
    }
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"Discord notification sent successfully: {response.getcode()}")
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"Discord rate limited: {e}")
        else:
            print(f"Failed to send Discord notification: {e}")

def main(token=None, discord_webhook=None):
    """Main orchestration loop to scan and update state."""
    seen_urls = load_seen_bounties()
    
    print(f"Scanning for bounties...")
    
    all_items = []
    
    for query in SEARCH_QUERIES:
        results = search_github(query, token)
        if results:
            items = results.get("items", [])
            all_items.extend(items)
            
    # Filter and process the combined list
    for item in all_items:
        if is_clean_candidate(item):
            url = item.get("html_url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                
    # Save updated state
    save_seen_bounties(seen_urls)
    
    # Send notification if there are new finds
    if seen_urls:
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        if discord_webhook:
            msg = f"🎯 **New Bounties Found:** {len(seen_urls)}\n**Time:** {current_time}"
            send_discord_notification(discord_webhook, msg)

if __name__ == "__main__":
    # Example usage logic, can be configured via env vars if desired
    main(token="ghp_...", discord_webhook="...")