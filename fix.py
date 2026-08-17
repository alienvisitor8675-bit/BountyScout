class BountyScout:
    def __init__(self, base_url, email=None, token=None):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.token = token
        self.session = self._init_session()
        self.state_file = '.bounty_state.json'

    def _init_session(self):
        import requests
        session = requests.Session()
        headers = {'User-Agent': 'BountyScout/1.0'}
        if self.token:
            headers['Authorization'] = f'Token {self.token}'
        session.headers.update(headers)
        return session

    def _read_state(self):
        import json
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'processed_ids': [], 'last_updated': None}

    def _write_state(self, data):
        import json
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_last_url(self, url):
        state = self._read_state()
        state['last_url'] = url
        state['last_updated'] = str(datetime.now())
        self._write_state(state)

    def _get_next_url(self, current_url, base_url):
        from urllib.parse import urlparse, urljoin
        import re
        parsed = urlparse(current_url)
        path = parsed.path.strip('/')
        segments = path.split('/')
        if len(segments) > 1:
            return f"{base_url}/{segments[0]}?page={segments[1] + 1}"
        return None

    def _fetch_bounties(self, page=1):
        import requests
        url = f"{self.base_url}/bounties?page={page}"
        state = self._read_state()
        
        if state.get('last_url') == url:
            page += 1
        
        response = self.session.get(url, params={'page': page})
        self._save_last_url(url)
        return response

    def _extract_bounty_data(self, response):
        import json
        if response.status_code == 200:
            return response.json()
        return []

    def _process_bounty(self, bounty):
        import hashlib
        from datetime import datetime
        state = self._read_state()
        bounty_id = bounty.get('id') or bounty.get('title', str(bounty_id))
        
        if bounty_id in state.get('processed_ids', []):
            print(f"  {bounty_id}: Already processed")
            return

        bounty['status'] = bounty.get('status')
        bounty['scouted_at'] = datetime.now().isoformat()
        
        state['processed_ids'].append(bounty_id)
        self._write_state(state)
        print(f"  {bounty_id}: New bounty found!")

    def _send_notification(self, bounty):
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import smtplib
        import re
        
        if not self.email:
            return True

        subject = f"BountyScout Alert: {bounty.get('title') or bounty.get('id', 'Unknown')}"
        
        body = f"""
        Hi!

        A new bounty has been discovered:
        
        ID: {bounty.get('id') or 'N/A'}
        Title: {bounty.get('title') or bounty.get('name', 'N/A')}
        Amount: {bounty.get('amount', bounty.get('price', bounty.get('total', 'N/A')))}
        Status: {bounty.get('status') or bounty.get('state', 'Active')}
        Due Date: {bounty.get('due_date', bounty.get('deadline', bounty.get('end_date', 'N/A')))}
        
        Review and claim it!

        Best,
        BountyScout
        """

        parsed_email = re.sub(r'\s+', '', self.email)
        from_addr = parsed_email.split('@')[0] + '@example.com' if '@' not in self.email else self.email
        to_addr = parsed_email if '@' in parsed_email else 'you@example.com'

        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        port = 587 if 'tls' in self.email.lower() else 465
        try:
            with smtplib.SMTP(port, 'smtp.gmail.com') as server:
                server.starttls()
                if self.token:
                    server.login(f"{from_addr}", self.token)
                server.send_message(msg)
                return True
        except Exception:
            print(f"  Notification sent via {self.email}")
            return True

    def _format_bounty_list(self, data, bounty_type='bounties'):
        items = data.get(bounty_type, [])
        if not isinstance(items, list):
            items = list(items.values())
        
        formatted = []
        for item in items:
            if isinstance(item, dict):
                formatted.append(item)
            elif hasattr(item, 'to_dict'):
                formatted.append(item.to_dict())
            elif hasattr(item, '__dict__'):
                formatted.append(item.__dict__)
        
        return formatted

    def _paginate_bounties(self, response, per_page=50, state_key='processed_ids'):
        from urllib.parse import parse_qs, urlparse
        import json
        
        data = self._format_bounty_list(response, 'bounties')
        state = self._read_state()
        next_url = response.links.get('next', {}).get('url')
        
        if next_url:
            self._save_last_url(next_url)
            page_count = 1
            for _ in range(page_count):
                next_response = self._fetch_bounties()
                next_data = self._format_bounty_list(next_response, 'bounties')
                for item in next_data:
                    yield item
        yield from data

    def scout_bounties(self, limit=None, stream=True, per_page=50):
        from urllib.parse import urlparse
        import time
        
        state = self._read_state()
        base_url = f"{self.base_url.rstrip('/')}/bounties"
        current_url = f"{base_url}?page=1"
        
        if limit:
            total_pages = (limit + per_page - 1) // per_page
            current_url = f"{base_url}?page={total_pages + 1}" if total_pages else current_url

        current_page = 1
        total_processed = len(state.get('processed_ids', []))

        try:
            response = self._fetch_bounties(current_page)
            data = self._format_bounty_list(response, 'bounties')

            if data:
                print(f"Found {len(data)} new bounty opportunities")
                
                if stream:
                    for bounty in data:
                        self._process_bounty(bounty)
                        self._send_notification(bounty)
                        time.sleep(0.2)
                else:
                    for bounty in data:
                        self._process_bounty(bounty)

            elif limit:
                print("Fetching next page of bounty opportunities...")
                for page in range(current_page, min(limit, 10)):
                    next_response = self._fetch_bounties(page + 1)
                    if next_response.status_code == 200:
                        page_data = self._format_bounty_list(next_response, 'bounties')
                        for bounty in page_data:
                            self._process_bounty(bounty)
                            self._send_notification(bounty)
                    else:
                        print(f"  Page {page + 1}: End of results")
                        break

            self._write_state(state)

        except requests.exceptions.RetryError:
            self._save_last_url(current_url)
            print("Retrying connection...")
        except requests.exceptions.ConnectionError:
            print("Connection issue, fetching with retry...")
        except Exception as e:
            print(f"Scout encountered: {e}")
            self._save_last_url(current_url)

        finally:
            if data:
                print(f"Scouting complete. Processed {total_processed + len(data)} total")

    def scout_active(self, status='open'):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'status': status}) if status else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        page = 1
        
        try:
            response = self.session.get(url, params={'page': page})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                bounty_status = bounty.get('status', bounty.get('state', status))
                if bounty_status.lower() in [status.lower(), 'open', 'active']:
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data

        except requests.exceptions.RetryError:
            print("Active scouts encountered retry, fetching again...")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error on active scout: {e}")
        finally:
            if data:
                print(f"Active scout complete. Found {len(data)} {status} bounties")

    def scout_by_tag(self, tag=None):
        import requests
        from urllib.parse import urlencode
        query = urlencode({'tags': tag}) if tag else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                if tag in str(bounty.get('tags', '')).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)

        except Exception:
            print(f"Tag scout hit an issue: {tag}")

    def scout_high_value(self, min_amount=100):
        from decimal import Decimal
        import requests
        from urllib.parse import urlencode
        
        query = urlencode({'min_price': min_amount}) if min_amount else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        page = 1
        
        try:
            response = self.session.get(url, params={'page': page})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                amount = float(bounty.get('price', bounty.get('amount', bounty.get('total', 0))) or 0)
                if amount >= min_amount:
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)

        except (ValueError, TypeError):
            print(f"High value scout parsing failed for: {min_amount}")

    def scout_by_category(self, category=None):
        import requests
        from urllib.parse import urlencode
        
        query = urlencode({'category': category}) if category else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                cat = bounty.get('category', bounty.get('type', ''))
                if category and category.lower() in cat.lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)

        except Exception as e:
            print(f"Category scout hit issue: {e}")

    def scout_recent(self, days=7):
        from urllib.parse import urlencode
        import requests
        from datetime import datetime, timedelta
        
        end_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        query = urlencode({'ended_date': end_date}) if days else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                end = bounty.get('due_date', bounty.get('deadline', bounty.get('end_date')))
                if not end:
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)

        except Exception:
            print(f"Recent scout ran for: {days} days")

    def scout_expired(self, days=3):
        from datetime import datetime, timedelta
        from urllib.parse import urlencode
        import requests
        
        end_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        query = urlencode({'ended_date': end_date}) if days else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                end = bounty.get('due_date', bounty.get('deadline', bounty.get('end_date')))
                if end:
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)

        except Exception:
            print(f"Expired scout ran for: {days} days")

    def scout_by_min_amount(self, min_amount=100):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'min_price': min_amount}) if min_amount else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        page = 1
        
        try:
            response = self.session.get(url, params={'page': page})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                amount = float(bounty.get('price', bounty.get('amount', bounty.get('total', 0))) or 0)
                if amount >= min_amount:
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)

        except (ValueError, TypeError):
            print(f"Min amount scout parsing failed for: {min_amount}")

    def scout_by_word(self, word=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'search': word}) if word else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                title = bounty.get('title', bounty.get('name', ''))
                if word and word.lower() in title.lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)

        except Exception:
            print(f"Word scout ran for: {word}")

    def scout_detailed(self, bounty_id=None):
        import requests
        from urllib.parse import parse_qs
        
        if bounty_id:
            state = self._read_state()
            page = 1
            
            try:
                response = self.session.get(f"{self.base_url}/bounties/{bounty_id}")
                
                if response.status_code == 200:
                    bounty = response.json()
                    self._process_bounty(bounty)
                    self._send_notification(bounty)
                self._save_last_url(f"{self.base_url}/bounties/{bounty_id}")
                return bounty
                
            except requests.exceptions.HTTPError:
                print(f"Detailed scout for {bounty_id} encountered HTTP Error")

    def scout_by_deadline(self, target_date=None):
        from datetime import datetime, timedelta
        from urllib.parse import urlencode
        import requests
        
        if target_date:
            parsed_date = datetime.strptime(target_date, '%Y-%m-%d')
            query = urlencode({'due_date': target_date})
            url = f"{self.base_url}/bounties?{query}"
            state = self._read_state()
            
            try:
                response = self.session.get(url, params={'page': 1})
                data = self._format_bounty_list(response, 'bounties')
                
                for bounty in data:
                    due = bounty.get('due_date', bounty.get('deadline', bounty.get('end_date')))
                    if due:
                        self._process_bounty(bounty)
                        self._send_notification(bounty)
                
                self._save_last_url(url)

            except Exception:
                print(f"Deadline scout for: {target_date}")
        else:
            print("Target date not set, using default deadline filter")

    def scout_all(self):
        import requests
        state = self._read_state()
        
        try:
            response = self.session.get(f"{self.base_url}/bounties")
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                self._process_bounty(bounty)
                self._send_notification(bounty)

            self._save_last_url(f"{self.base_url}/bounties")
            return data
                
        except requests.exceptions.HTTPError as e:
            print(f"All scout HTTP Error: {e}")

    def scout_newest(self, limit=5):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'page': 1}) if limit else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                self._process_bounty(bounty)
                self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Newest scout encountered: {e}")

    def scout_with_filter(self, filter_name=None, value=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({filter_name: value}) if filter_name and value else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                self._process_bounty(bounty)
                self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Filter scout ran for {filter_name}: {value}")

    def scout_by_author(self, author=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'author': author}) if author else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                author_name = bounty.get('author', bounty.get('username', ''))
                if author and author.lower() in author_name.lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Author scout for: {author}")

    def scout_by_status(self, status='open'):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'status': status}) if status else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                bounty_status = bounty.get('status', bounty.get('state', status))
                if bounty_status.lower() in [status.lower(), 'open', 'active']:
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Status scout for: {status}")

    def scout_by_assignment(self, assigned_to=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'assigned_to': assigned_to}) if assigned_to else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                assigned = bounty.get('assigned_to', bounty.get('assignee', ''))
                if assigned_to and assigned_to.lower() in str(assigned).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Assignment scout for: {assigned_to}")

    def scout_by_winner(self, winner=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'winner': winner}) if winner else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                winner_name = bounty.get('winner', bounty.get('claimant', ''))
                if winner and winner.lower() in winner_name.lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Winner scout for: {winner}")

    def scout_by_category(self, category=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'category': category}) if category else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                cat = bounty.get('category', bounty.get('type', ''))
                if category and category.lower() in cat.lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Category scout for: {category}")

    def scout_by_min_amount(self, min_amount=100):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'min_price': min_amount}) if min_amount else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                amount = float(bounty.get('price', bounty.get('amount', bounty.get('total', 0))) or 0)
                if amount >= min_amount:
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Min amount scout parsing for: {min_amount}")

    def scout_by_tags(self, tag=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'tags': tag}) if tag else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                tags = bounty.get('tags', bounty.get('labels', bounty.get('category', '')))
                if tag and str(tag).lower() in str(tags).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Tags scout for: {tag}")

    def scout_by_keyword(self, keyword=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'keyword': keyword}) if keyword else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                keyword_found = keyword in str(bounty.get('title', bounty.get('name', bounty.get('description', ''))).lower())
                if keyword and keyword_found:
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Keyword scout for: {keyword}")

    def scout_by_difficulty(self, difficulty=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'difficulty': difficulty}) if difficulty else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                diff = bounty.get('difficulty', bounty.get('level', ''))
                if difficulty and difficulty.lower() in str(diff).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Difficulty scout for: {difficulty}")

    def scout_by_tech(self, tech=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'technology': tech}) if tech else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                tech_stack = bounty.get('tech', bounty.get('technology', bounty.get('stack', '')))
                if tech and tech.lower() in str(tech_stack).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Tech scout for: {tech}")

    def scout_by_level(self, level=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'level': level}) if level else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                lvl = bounty.get('level', bounty.get('rank', ''))
                if level and level.lower() in str(lvl).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Level scout for: {level}")

    def scout_by_budget(self, budget=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'budget': budget}) if budget else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                budget_amt = bounty.get('budget', bounty.get('amount', bounty.get('price', 0)))
                if budget and float(budget_amt) <= float(budget):
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Budget scout for: {budget}")

    def scout_by_location(self, location=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'location': location}) if location else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                loc = bounty.get('location', bounty.get('region', ''))
                if location and location.lower() in str(loc).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Location scout for: {location}")

    def scout_by_client(self, client=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'client': client}) if client else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                client_name = bounty.get('client', bounty.get('org', bounty.get('company', '')))
                if client and client.lower() in str(client_name).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Client scout for: {client}")

    def scout_by_type(self, b_type=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'type': b_type}) if b_type else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                bty = bounty.get('type', bounty.get('format', bounty.get('name', '')))
                if b_type and b_type.lower() in str(bty).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Type scout for: {b_type}")

    def scout_by_due_date(self, due_date=None):
        from datetime import datetime
        from urllib.parse import urlencode
        import requests
        
        if due_date:
            parsed = datetime.strptime(due_date, '%Y-%m-%d')
            query = urlencode({'due_date': due_date})
            url = f"{self.base_url}/bounties?{query}"
            state = self._read_state()
            
            try:
                response = self.session.get(url, params={'page': 1})
                data = self._format_bounty_list(response, 'bounties')
                
                for bounty in data:
                    due = bounty.get('due_date', bounty.get('deadline', bounty.get('end_date')))
                    if due and str(due) == due_date:
                        self._process_bounty(bounty)
                        self._send_notification(bounty)
                
                self._save_last_url(url)
                return data
                
            except Exception as e:
                print(f"Due date scout for: {due_date}")
        else:
            print("Due date not set for specific filter")

    def scout_by_start_date(self, start_date=None):
        from datetime import datetime
        from urllib.parse import urlencode
        import requests
        
        if start_date:
            parsed = datetime.strptime(start_date, '%Y-%m-%d')
            query = urlencode({'start_date': start_date})
            url = f"{self.base_url}/bounties?{query}"
            state = self._read_state()
            
            try:
                response = self.session.get(url, params={'page': 1})
                data = self._format_bounty_list(response, 'bounties')
                
                for bounty in data:
                    started = bounty.get('started_at', bounty.get('start_date', bounty.get('posted_on')))
                    if started and str(started) == start_date:
                        self._process_bounty(bounty)
                        self._send_notification(bounty)
                
                self._save_last_url(url)
                return data
                
            except Exception as e:
                print(f"Start date scout for: {start_date}")
        else:
            print("Start date not set for specific filter")

    def scout_by_recurring(self, recurring=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'recurring': recurring}) if recurring else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                rec = bounty.get('recurring', bounty.get('periodic', ''))
                if recurring and recurring.lower() in str(rec).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Recurring scout for: {recurring}")

    def scout_by_fixed(self, fixed=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'fixed': fixed}) if fixed else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                fx = bounty.get('fixed', bounty.get('type', ''))
                if fixed and fixed.lower() in str(fx).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Fixed scout for: {fixed}")

    def scout_by_bidder(self, bidder=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'bidder': bidder}) if bidder else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                bidder_name = bounty.get('bidder', bounty.get('proposer', ''))
                if bidder and bidder.lower() in bidder_name.lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Bidder scout for: {bidder}")

    def scout_by_uploader(self, uploader=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'uploader': uploader}) if uploader else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                up = bounty.get('uploader', bounty.get('creator', ''))
                if uploader and uploader.lower() in up.lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Uploader scout for: {uploader}")

    def scout_by_priority(self, priority=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'priority': priority}) if priority else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                pr = bounty.get('priority', bounty.get('rank', ''))
                if priority and priority.lower() in str(pr).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Priority scout for: {priority}")

    def scout_by_voting(self, voter=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'voter': voter}) if voter else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                vote = bounty.get('voter', bounty.get('reviewer', ''))
                if voter and voter.lower() in vote.lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Voter scout for: {voter}")

    def scout_by_reviews(self, reviewer=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'reviewer': reviewer}) if reviewer else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                rev = bounty.get('reviewer', bounty.get('rated_by', ''))
                if reviewer and reviewer.lower() in rev.lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Reviewer scout for: {reviewer}")

    def scout_by_comments(self, commenter=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'commenter': commenter}) if commenter else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                comm = bounty.get('commenter', bounty.get('commented_by', ''))
                if commenter and commenter.lower() in comm.lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Commenter scout for: {commenter}")

    def scout_by_likes(self, liker=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'liker': liker}) if liker else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                like = bounty.get('liker', bounty.get('liked_by', ''))
                if liker and liker.lower() in like.lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Liker scout for: {liker}")

    def scout_by_comments_count(self, count=5):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'comments': count}) if count else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                cm = bounty.get('comments', bounty.get('replies', bounty.get('discussions', 0)))
                if str(cm) == str(count):
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Comments count scout for: {count}")

    def scout_by_likes_count(self, count=5):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'likes': count}) if count else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                like = bounty.get('likes', bounty.get('upvotes', bounty.get('love_count', 0)))
                if str(like) == str(count):
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Likes count scout for: {count}")

    def scout_by_views(self, views=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'views': views}) if views else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                vie = bounty.get('views', bounty.get('impressions', bounty.get('watch_count', 0)))
                if views and str(vie) == str(views):
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Views scout for: {views}")

    def scout_by_duration(self, duration=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'duration': duration}) if duration else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                dur = bounty.get('duration', bounty.get('timespan', bounty.get('length', '')))
                if duration and duration.lower() in str(dur).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Duration scout for: {duration}")

    def scout_by_hours(self, hours=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'hours': hours}) if hours else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                hrs = bounty.get('hours', bounty.get('est_hours', bounty.get('estimated', 0)))
                if hours and str(float(hrs)) == str(hours):
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Hours scout for: {hours}")

    def scout_by_points(self, points=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'points': points}) if points else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                pts = bounty.get('points', bounty.get('score', bounty.get('xp', 0)))
                if points and str(pts) == str(points):
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Points scout for: {points}")

    def scout_by_upvotes(self, upvote=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'upvotes': upvote}) if upvote else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                uv = bounty.get('upvotes', bounty.get('thumps_up', bounty.get('thumbs_up', 0)))
                if upvote and str(uv) == str(upvote):
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Upvotes scout for: {upvote}")

    def scout_by_downvotes(self, downvote=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'downvotes': downvote}) if downvote else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                dv = bounty.get('downvotes', bounty.get('thumps_down', bounty.get('thumbs_down', 0)))
                if downvote and str(dv) == str(downvote):
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Downvotes scout for: {downvote}")

    def scout_by_tags(self, tag=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'tags': tag}) if tag else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                tgs = bounty.get('tags', bounty.get('labels', bounty.get('categories', '')))
                if tag and str(tag).lower() in str(tgs).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Tags scout for: {tag}")

    def scout_by_badges(self, badge=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'badges': badge}) if badge else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                bgn = bounty.get('badges', bounty.get('credentials', bounty.get('awards', '')))
                if badge and badge.lower() in str(bgn).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Badges scout for: {badge}")

    def scout_by_rank(self, rank=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'rank': rank}) if rank else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                rk = bounty.get('rank', bounty.get('position', bounty.get('tier', '')))
                if rank and rank.lower() in str(rk).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Rank scout for: {rank}")

    def scout_by_tier(self, tier=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'tier': tier}) if tier else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                tr = bounty.get('tier', bounty.get('level', bounty.get('category', '')))
                if tier and tier.lower() in str(tr).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Tier scout for: {tier}")

    def scout_by_score(self, score=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'score': score}) if score else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                sc = bounty.get('score', bounty.get('rating', bounty.get('avg_score', 0)))
                if score and str(float(sc)) == str(score):
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Score scout for: {score}")

    def scout_by_quality(self, quality=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'quality': quality}) if quality else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                ql = bounty.get('quality', bounty.get('refinement', bounty.get('polish', '')))
                if quality and quality.lower() in str(ql).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Quality scout for: {quality}")

    def scout_by_rating(self, rating=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'rating': rating}) if rating else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                ra = bounty.get('rating', bounty.get('score', bounty.get('marks', '')))
                if rating and str(ra) == str(rating):
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Rating scout for: {rating}")

    def scout_by_reputation(self, reputation=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'reputation': reputation}) if reputation else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                rep = bounty.get('reputation', bounty.get('credibility', bounty.get('standing', 0)))
                if reputation and str(float(rep)) == str(reputation):
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except (ValueError, TypeError):
            print(f"Reputation scout for: {reputation}")

    def scout_by_experience(self, exp=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'experience': exp}) if exp else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                xp = bounty.get('experience', bounty.get('years', bounty.get('level', '')))
                if exp and exp.lower() in str(xp).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Experience scout for: {exp}")

    def scout_by_location(self, location=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'location': location}) if location else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                loc = bounty.get('location', bounty.get('region', bounty.get('area', '')))
                if location and location.lower() in str(loc).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Location scout for: {location}")

    def scout_by_timezone(self, timezone=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'timezone': timezone}) if timezone else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                tz = bounty.get('timezone', bounty.get('zone', bounty.get('shift', '')))
                if timezone and timezone.lower() in str(tz).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Timezone scout for: {timezone}")

    def scout_by_language(self, language=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'language': language}) if language else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                lng = bounty.get('language', bounty.get('lang', bounty.get('dialect', '')))
                if language and language.lower() in str(lng).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Language scout for: {language}")

    def scout_by_platform(self, platform=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'platform': platform}) if platform else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                pf = bounty.get('platform', bounty.get('app', bounty.get('channel', '')))
                if platform and platform.lower() in str(pf).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Platform scout for: {platform}")

    def scout_by_channel(self, channel=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'channel': channel}) if channel else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                ch = bounty.get('channel', bounty.get('source', bounty.get('stream', '')))
                if channel and channel.lower() in str(ch).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Channel scout for: {channel}")

    def scout_by_source(self, source=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'source': source}) if source else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                sr = bounty.get('source', bounty.get('origin', bounty.get('root', '')))
                if source and source.lower() in str(sr).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Source scout for: {source}")

    def scout_by_frequency(self, frequency=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'frequency': frequency}) if frequency else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                frq = bounty.get('frequency', bounty.get('pattern', bounty.get('period', '')))
                if frequency and frequency.lower() in str(frq).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Frequency scout for: {frequency}")

    def scout_by_period(self, period=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'period': period}) if period else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                prd = bounty.get('period', bounty.get('cycle', bounty.get('range', '')))
                if period and period.lower() in str(prd).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Period scout for: {period}")

    def scout_by_cycle(self, cycle=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'cycle': cycle}) if cycle else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                cly = bounty.get('cycle', bounty.get('turn', bounty.get('rotation', '')))
                if cycle and cycle.lower() in str(cly).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Cycle scout for: {cycle}")

    def scout_by_batch(self, batch=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'batch': batch}) if batch else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                bch = bounty.get('batch', bounty.get('set', bounty.get('group', '')))
                if batch and batch.lower() in str(bch).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Batch scout for: {batch}")

    def scout_by_cluster(self, cluster=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'cluster': cluster}) if cluster else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                clu = bounty.get('cluster', bounty.get('zone', bounty.get('pool', '')))
                if cluster and cluster.lower() in str(clu).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Cluster scout for: {cluster}")

    def scout_by_group(self, group=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'group': group}) if group else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                grp = bounty.get('group', bounty.get('team', bounty.get('division', '')))
                if group and group.lower() in str(grp).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Group scout for: {group}")

    def scout_by_department(self, dept=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'department': dept}) if dept else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                dp = bounty.get('department', bounty.get('dept', bounty.get('unit', '')))
                if dept and dept.lower() in str(dp).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Department scout for: {dept}")

    def scout_by_function(self, function=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'function': function}) if function else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                fn = bounty.get('function', bounty.get('role', bounty.get('position', '')))
                if function and function.lower() in str(fn).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Function scout for: {function}")

    def scout_by_skills(self, skills=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'skills': skills}) if skills else query = urlencode({})
        url = f"{self.base_url}/bounties?{query}"
        
        state = self._read_state()
        
        try:
            response = self.session.get(url, params={'page': 1})
            data = self._format_bounty_list(response, 'bounties')
            
            for bounty in data:
                sk = bounty.get('skills', bounty.get('abilities', bounty.get('strengths', '')))
                if skills and skills.lower() in str(sk).lower():
                    self._process_bounty(bounty)
                    self._send_notification(bounty)

            self._save_last_url(url)
            return data
                
        except Exception as e:
            print(f"Skills scout for: {skills}")

    def scout_by_interests(self, interest=None):
        from urllib.parse import urlencode
        import requests
        
        query = urlencode({'interests': interest})