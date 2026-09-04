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
                elif isinstance(data, dict) and "items" in data:
                    return set(data["items"])
        except Exception as e:
            print(f"Error loading state file: {e}")
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
    params = {'q': query, 'per_page': 15}
    url = f"https://api.github.com/search/issues?{urllib.parse.urlencode(params)}"
    
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
            # Ensure we return the items list for easy iteration
            if "items" in data:
                return data
            return {}
    except Exception as e:
        print(f"GitHub Search API Error for query '{query}': {e}")
        return {}


def is_clean_candidate(item):
    """Triage logic to filter out noisy, assigned, closed, or spam tasks."""
    # 1. Skip if thread is overcrowded (highly competitive)
    comments = int(item.get("comments", 0))
    if comments > MAX_COMMENTS:
        return False

    # 2. Skip if already assigned
    assignees = item.get("assignees")
    if assignees and len(assignees) > 0:
        return False
    
    # 3. Skip if the item itself is a raw Pull Request type (though search merges them)
    if "pull_request" in item:
        # Optional: Check if the PR body is relevant, else skip
        # return False  # Uncomment to filter PRs strictly
        pass
    
    title = str(item.get("title", "")).strip().lower()
    body = str(item.get("body", "")).strip().lower()
    
    # 4. Skip cryptocurrency/article writing/spam keywords
    blocklist = [
        "airdrop", "referral", "casino", "gambling", "trading bot", 
        "blog post", "article writing", "tutorial proposal", "content creator"
    ]
    
    if title and body:
        # Optimization: Check if keywords exist in the text
        for term in blocklist:
            if term in title or term in body:
                return False
    elif title and any(term in title for term in blocklist):
        return False
    elif body and any(term in body for term in blocklist):
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
            print("Telegram notification sent successfully.")
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
            if response.status == 200:
                print("Discord notification sent successfully.")
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")


if __name__ == "__main__":
    seen_bounties = load_seen_bounties()
    
    found_bounties = []
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    for query in SEARCH_QUERIES:
        results = search_github(query)
        if results.get("items"):
            for item in results["items"]:
                if is_clean_candidate(item):
                    # Construct a clean URL for deduplication
                    repo_full_name = item.get("repository", {}).get("full_name", "")
                    issue_number = item.get("number", "")
                    full_url = f"https://github.com/{repo_full_name}/issues/{issue_number}"
                    
                    if full_url not in seen_bounties:
                        found_bounties.append(item)
                        seen_bounties.add(full_url)
                        print(f"Found: {full_url}")
    
    # Save state
    save_seen_bounties(seen_bounties)
    
    # Prepare notification message
    if found_bounties:
        message = f"🎯 Bounty Alert: {len(found_bounties)} New Opportunities found\n**Scan Time:** {current_time}\n"
        
        for i, item in enumerate(found_bounties, 1):
            repo = item.get("repository", {}).get("full_name", "Unknown")
            num = item.get("number", "N/A")
            title = item.get("title", "No Title")
            comments = item.get("comments", 0)
            updated = item.get("updated_at", "Just Now")
            
            message += f"\n#### {i}. [{title}]({repo}/issues/{num})\n"
            message += f"- **Comments:** {comments}\n"
            message += f"- **Last Updated:** {updated}\n"
        
        # Send Notifications
        if os.path.exists("telegram_config.json"):
            import telegram_config
            send_telegram_notification(telegram_config.token, telegram_config.chat_id, message)
        
        send_discord_notification("https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN", message)
    else:
        print("No new bounties found.")