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
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"GitHub Search API Error for query '{query}': {e}")
        return {}


def is_clean_candidate(item):
    """Triage logic to filter out noisy, assigned, closed, or spam tasks."""
    # 1. Skip if already a Pull Request (or has pull_request metadata)
    if "pull_request" in item:
        return False
    # 2. Skip if already assigned
    if item.get("assignees"):
        return False
    # 3. Skip if thread is overcrowded (highly competitive)
    if int(item.get("comments", 0)) > MAX_COMMENTS:
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
            response.read()  # Consume stream to prevent buffering issues
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
            response.read()
            print("Discord notification sent successfully.")
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")


# Main Execution Logic (To ensure 'complete' functionality)
def scout_bounties(token=None, discord_webhook=None, telegram_token=None, telegram_chat_id=None):
    """Orchestrate the bounty scanning process."""
    seen_bounties = load_seen_bounties()
    new_bounties_count = 0
    
    # Construct the notification message
    scan_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    notification_text = f"🎯 Bounty Alert: {new_bounties_count} New Opportunity(ies) found"
    
    # Prepare the full message
    message_parts = [f"**Scan Time:** {scan_time}"]

    # Iterate through search queries
    for query in SEARCH_QUERIES:
        results = search_github(query, token)
        
        if "items" in results:
            for item in results["items"]:
                if is_clean_candidate(item):
                    # Build the link
                    url = item.get("html_url", "#")
                    title = item.get("title", "Untitled")
                    
                    # Build the rich text
                    title_text = f"[[Bounty: {title}]] ({url})"
                    body_line = f"- **Repository:** {item.get('repository', {}).get('html_url', '#')}"
                    comments = item.get("comments", 0)
                    updated = item.get("updated_at", "")
                    last_line = f"- **Comments:** {comments}"
                    
                    # Append to message
                    notification_text += f"\n{title_text}"
                    notification_text += f"- **Repository:** {item.get('repository', {}).get('html_url', '#')}"
                    notification_text += f"- **Comments:** {comments}"
                    notification_text += f"- **Last Updated:** {updated}"
                    
                    # Update state
                    seen_bounties.add(url)
                    new_bounties_count += 1
                    
            # Print results for state saving
            if results.get("total_count", 0) > 0:
                print(f"Found {results.get('total_count')} items for query: {query}")

    # Update state
    save_seen_bounties(seen_bounties)

    # Trigger Notifications if found
    if new_bounties_count > 0:
        print(f"Processing {new_bounties_count} new bounties...")
        # Note: Logic to format a large block of text for Telegram vs Discord can vary
        # For simplicity, we pass the accumulated text
        if discord_webhook:
            send_discord_notification(discord_webhook, notification_text)
        
        if telegram_token and telegram_chat_id:
            send_telegram_notification(telegram_token, telegram_chat_id, notification_text)
            
    return new_bounties_count


if __name__ == "__main__":
    scout_bounties()