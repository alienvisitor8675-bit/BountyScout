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
                # Handle if data is a flat list (most common) or a nested dict
                if isinstance(data, list):
                    return set(data)
                elif isinstance(data, dict):
                    # Fallback for nested structures like {"bounties": [...]}
                    return set(data.get("bounties", []))
                else:
                    return set(data)
        except json.JSONDecodeError as e:
            print(f"Error loading state file (JSON): {e}")
            # Fallback to empty set or re-reading
            return set()
        except Exception as e:
            print(f"Error loading state file: {e}")
    return set()

def save_seen_bounties(seen_urls):
    """Save the updated list of seen bounty URLs."""
    try:
        # Convert set to list for JSON serialization if needed
        data_to_save = list(seen_urls)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2)
    except Exception as e:
        print(f"Error saving state file: {e}")

def search_github(query, token=None):
    """Fetch search results from GitHub Issues API."""
    encoded_params = urllib.parse.urlencode({'q': query, 'per_page': 15})
    url = f"https://api.github.com/search/issues?{encoded_params}"
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
        print(f"GitHub Search API HTTP Error for query '{query}': {e}")
        return {}
    except Exception as e:
        print(f"GitHub Search API Error for query '{query}': {e}")
        return {}

def is_clean_candidate(item):
    """Triage logic to filter out noisy, assigned, closed, or spam tasks."""
    if not item:
        return False
    
    # 1. Skip if already a Pull Request (Check nested key)
    if item.get("pull_request"):
        return False
    
    # 2. Skip if already assigned
    assignees = item.get("assignees")
    if assignees:
        return False
    
    # 3. Skip if thread is overcrowded (highly competitive)
    try:
        comments = int(item.get("comments", 0))
        if comments > MAX_COMMENTS:
            return False
    except (ValueError, TypeError):
        pass  # Fallback if comments is a string or object
        
    title = str(item.get("title", "")).lower()
    body = str(item.get("body", "")).lower()
    
    # 4. Skip cryptocurrency/article writing/spam keywords
    blocklist = [
        "airdrop", "referral", "casino", "gambling", "trading bot", 
        "blog post", "article writing", "tutorial proposal", "content creator"
    ]
    
    for term in blocklist:
        if term in title or term in body:
            # Optionally limit matches to a reasonable length to avoid false positives
            if title == term or body == term:
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
            # Consumes the response (optional but good for debugging)
            _ = response.read()
            print("Telegram notification sent successfully.")
            return True
    except urllib.error.HTTPError as e:
        print(f"Telegram HTTP Error: {e}")
        return False
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
            # Check status code to ensure it's 200 OK (Webhook standard)
            status = response.status
            # Optionally read body to ensure consumption, or just return status
            if status == 200:
                print("Discord notification sent successfully.")
            return True
    except urllib.error.HTTPError as e:
        print(f"Discord HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")
        return True # Return True to avoid breaking loop even on timeout

def get_bounty_details(item):
    """Generate a human-readable string from a GitHub issue item."""
    url = item.get("html_url", "Unknown URL")
    title = item.get("title", "Untitled")
    repo = item.get("repository")
    repo_url = repo.get("html_url", repo.get("name", "Unknown Repo")) if repo else repo_url
    repo_url = repo_url if repo_url else repo.get("owner", {}).get("login", "")
    
    return {
        "title": title,
        "url": url,
        "repo": repo_url,
        "comments": item.get("comments", 0),
        "updated": item.get("updated_at", datetime.now(timezone.utc).isoformat())
    }

def run_bounty_scout(token=None):
    """Main orchestration function."""
    print(f"Loading seen bounties...")
    seen_urls = load_seen_bounties()
    
    all_bounties = {}
    
    print(f"Scanning {len(SEARCH_QUERIES)} queries...")
    for idx, query in enumerate(SEARCH_QUERIES):
        print(f"  Query {idx + 1}: {query[:50]}...")
        results = search_github(query, token)
        
        if results and "items" in results:
            for item in results["items"]:
                if is_clean_candidate(item):
                    url = item.get("html_url")
                    # Store with normalized key to avoid duplicates in seen_urls
                    seen_urls.add(url)
                    title = item.get("title", f"Bounty #{len(all_bounties) + 1}")
                    all_bounties[title] = item
            
            if all_bounties:
                break # Found new ones, stop early to save cycles (optional)
    
    # Save updated state
    save_seen_bounties(seen_urls)
    
    if all_bounties:
        # Determine output channel (simplified for this script)
        print(f"Found {len(all_bounties)} new bounties!")
        # Logic to send notification based on count
        count = len(all_bounties)
        if count > 0:
            msg = f"🎯 Bounty Alert: {count} New Opportunity{'ies' if count != 1 else ''} found!"
            send_telegram_notification(token, "123456", msg) # Example logic
            # send_discord_notification(webhook_url, msg)
    
    return all_bounties

# Initialize state if file doesn't exist
if not os.path.exists(STATE_FILE):
    save_seen_bounties(seen_urls=load_seen_bounties())

if __name__ == "__main__":
    # Example run
    results = run_bounty_scout(token="ghp_your_token_here")
    print(f"Scan complete. Found: {len(results)} items.")