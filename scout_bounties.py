import json
import os
import urllib.request
import urllib.parse
import re
from datetime import datetime, timezone

# Configuration
STATE_FILE = "seen_bounties.json"
MAX_COMMENTS = 25 # Filter out overcrowded threads

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
                    # Fallback if saved in a nested format (e.g., from a legacy dump)
                    return set(data.get("items", data.get("urls", [])))
        except json.JSONDecodeError as e:
            print(f"Error loading state file JSON: {e}")
            return set()
        except Exception as e:
            print(f"Error loading state file: {e}")
            return set()
    return set()

def save_seen_bounties(seen_urls):
    """Save the updated list of seen bounty URLs."""
    try:
        # Ensure we have a list of strings
        urls_to_save = list(set(seen_urls))
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(urls_to_save, f, indent=2)
    except Exception as e:
        print(f"Error saving state file: {e}")

def search_github(query, token=None):
    """Fetch search results from GitHub Issues API."""
    base_url = f"https://api.github.com/search/issues"
    params = {'q': query, 'per_page': 15}
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
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
            # Handle 200 No Content or empty response
            data = response.read().decode("utf-8")
            if data:
                return json.loads(data)
            else:
                return {}
    except urllib.error.HTTPError:
        # Catch 404/409/502 etc gracefully
        return {}
    except Exception as e:
        print(f"GitHub Search API Error for query '{query}': {e}")
        return {}

def is_clean_candidate(item):
    """Triage logic to filter out noisy, assigned, closed, or spam tasks."""
    if not item:
        return False
    
    # 1. Skip if already a Pull Request (handled by is:issue mostly, but filter safety)
    # In search_issues, pull_request is often a nested dict.
    if "pull_request" in item and item["pull_request"]["merged"]:
        return False
        
    # 2. Skip if already assigned to someone (optional filter)
    assignees = item.get("assignees")
    if assignees and len(assignees) > 0:
        return False
    
    # 3. Skip if thread is overcrowded
    comments = item.get("comments", 0)
    if isinstance(comments, int) and comments > MAX_COMMENTS:
        return False
    
    title = str(item.get("title", "")).lower()
    body = str(item.get("body", "")).lower()
    
    # 4. Skip cryptocurrency/article writing/spam keywords
    blocklist = [
        "airdrop", "referral", "casino", "gambling", "trading bot", 
        "blog post", "article writing", "tutorial proposal", "content creator"
    ]
    
    # Use regex for case-insensitive check or simple 'in'
    for term in blocklist:
        if term in title or term in body:
            return False
        
    return True

def send_telegram_notification(token, chat_id, message):
    """Send a notification message via Telegram Bot API."""
    if not token or not chat_id:
        return
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
            if response.status == 200:
                print("Telegram notification sent successfully.")
    except urllib.error.HTTPError as e:
        # Handle rate limiting or status codes
        print(f"Telegram HTTP Error: {e}")
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")

def send_discord_notification(webhook_url, message):
    """Send a notification message via Discord Webhook."""
    if not webhook_url:
        return
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
    except urllib.error.HTTPError:
        # Discord Webhooks can return 204 No Content on success sometimes
        pass
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

def generate_report(title, items, scan_time):
    """Helper to format the output markdown."""
    report_lines = [f"{title}", "", "**Scan Time:**", f"{scan_time}", ""]
    
    for i, item in enumerate(items):
        if not item:
            continue
        
        repo = item.get("repository", {}).get("name", "unknown")
        url = item.get("html_url", "#")
        comments = item.get("comments", 0)
        last_updated = item.get("updated_at", "")
        
        report_lines.append(f"#### {i + 1}. [{url}]")
        report_lines.append(f"- **Repository:** [`{repo}`]({url})")
        report_lines.append(f"- **Comments:** `{comments}`")
        report_lines.append(f"- **Last Updated:** `{last_updated}`")
        report_lines.append("")
        
    return "\n".join(report_lines)

if __name__ == "__main__":
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "123456789")
    
    # Load seen bounties
    seen_bounties = load_seen_bounties()
    
    # Scan all queries
    all_items = []
    for query in SEARCH_QUERIES:
        results = search_github(query, token=token)
        if results and "items" in results:
            all_items.extend(results["items"])
        elif results:
             all_items.extend(results.get("items", []))

    # Deduplicate based on raw URL and filter for clean candidates
    cleaned_items = []
    for item in all_items:
        if is_clean_candidate(item):
            url = item.get("html_url")
            # Add to seen set to prevent double counting in next run
            seen_bounties.add(url)
            cleaned_items.append(item)
            
            # Limit to 25 per run logic, but MAX_COMMENTS handles thread crowding
            if len(cleaned_items) > MAX_COMMENTS:
                break

    # Save state
    save_seen_bounties(seen_bounties)
    
    # Generate and Send Report
    scan_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report_title = "🎯 Bounty Alert: New Opportunities Found"
    report = generate_report(report_title, cleaned_items, scan_time)
    
    if report:
        send_discord_notification(os.getenv("DISCORD_WEBHOOK_URL", ""), report)
        send_telegram_notification(token, chat_id, report)
        
        # Print locally for debugging
        print(report)