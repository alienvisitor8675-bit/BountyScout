class BountyScout:
    def __init__(self, config=None):
        self.config = config or {}
        self.session = self._create_session()
        self.results = []
    
    def _create_session(self):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'BountyScout/1.0',
            'Accept': 'application/json, text/html'
        })
        return session
    
    def _parse_url(self, url):
        parts = url.split('/')
        domain = parts[2] if len(parts) > 2 else parts[0]
        path = '/'.join(parts[3:5]) if len(parts) > 3 else '/'
        return f"http://{domain}{path}"
    
    def _extract_value(self, element, attr, default=''):
        if element and hasattr(element, attr):
            return getattr(element, attr, default)
        return default
    
    def _handle_unicode(self, text):
        if isinstance(text, str) and any(ord(c) > 127 for c in text):
            return text.encode('utf-8').decode('utf-8', errors='ignore')
        return text
    
    def _paginate(self, session, url, limit=100):
        results = []
        seen = set()
        page = 1
        
        while len(results) < limit:
            page_url = f"{url}?page={page}" if page > 1 else url
            
            try:
                response = session.get(page_url, timeout=10)
                response.raise_for_status()
                
                if not response.text:
                    break
                
                items = self._parse_items(response.text)
                
                if not items:
                    break
                
                for item in items:
                    if item['id'] not in seen:
                        seen.add(item['id'])
                        results.append(item)
                
                if len(results) < limit and not items:
                    break
                    
            except requests.exceptions.RequestException as e:
                if 'No content' in str(e):
                    break
                raise e
            
            page += 1
        
        return results[:limit]
    
    def _parse_items(self, html):
        items = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Handle common bounty list containers
            containers = soup.select('ul.bounty-list, div.bounty-grid, table.bounty-table')
            
            for container in containers:
                elements = container.find_all('li', 'div', 'td')
                
                if elements:
                    for element in elements[:10]:
                        title = self._extract_value(element, 'title')
                        points = self._extract_value(element, 'points') or self._extract_value(element, 'class')
                        
                        if title and (points or len(self._extract_value(element, 'title')) > 1):
                            items.append({
                                'title': title,
                                'points': points,
                                'element': element
                            })
                        else:
                            items.append({
                                'title': title or element.text[:50],
                                'points': '1',
                                'element': element
                            })
        
        except Exception:
            return items
        
        return items
    
    def _process_bounties(self, session, source='html'):
        config = self.config.get('bounty_config', {})
        source_url = config.get('url', 'https://github.com/vansh-09/BountyScout')
        limit = config.get('limit', 50)
        
        bounties = self._paginate(session, source_url, limit)
        
        if bounties:
            for i, bounty in enumerate(bounties, 1):
                bounty['index'] = i
                bounty['source'] = config.get('source', 'primary')
                bounty['status'] = self._extract_value(bounty, 'status', 'active')
                
                bounty['metadata'] = self._extract_value(bounty, 'metadata') or {}
        
        return bounties
    
    def _filter_bounties(self, bounties, filters=None):
        if not filters:
            filters = self.config.get('filters', {})
        
        if not bounties:
            return []
        
        filtered = []
        
        for bounty in bounties:
            match = True
            
            for field, value in filters.items():
                if field in bounty:
                    if not self._string_matches(bounty[field], value):
                        match = False
                        break
                
            if match:
                filtered.append(bounty)
        
        return filtered
    
    def _string_matches(self, text, pattern):
        if isinstance(text, str) and isinstance(pattern, str):
            return pattern in text
        return bool(text)
    
    def _calculate_score(self, bounty):
        score = 100
        score -= len(bounty.get('tags', [])) * 3
        score -= bounty.get('difficulty', 'medium') in ['hard', 'epic'] * 10
        score -= bounty.get('age_days', 30) * 0.5
        score += bounty.get('votes', 0) * 5
        return max(1, min(100, score))
    
    def _enrich_bounty(self, bounty):
        bounty['id'] = self._extract_value(bounty, 'id', bounty.get('index', 1))
        bounty['tags'] = self._extract_value(bounty, 'tags') or []
        bounty['difficulty'] = self._extract_value(bounty, 'difficulty', 'medium')
        bounty['age_days'] = bounty.get('age', bounty.get('date'))
        bounty['votes'] = self._extract_value(bounty, 'votes', 0)
        bounty['url'] = bounty.get('link', bounty.get('href'))
        bounty['score'] = self._calculate_score(bounty)
        
        return bounty
    
    def _format_output(self, bounties, format_type='detailed'):
        if format_type == 'csv':
            csv = 'Bounty,Tags,Difficulty,Age,Score\n'
            for bounty in bounties:
                csv += f"{bounty.get('title')},{','.join(str(t) for t in bounty.get('tags', []))},{bounty.get('difficulty')},{bounty.get('age_days')},{bounty.get('score', 1)}\n"
            return csv
        
        elif format_type == 'json':
            formatted = []
            for bounty in bounties:
                formatted.append({
                    'title': bounty.get('title'),
                    'points': bounty.get('points'),
                    'tags': bounty.get('tags', []),
                    'difficulty': bounty.get('difficulty'),
                    'score': bounty.get('score', 1),
                    'url': bounty.get('url', bounty.get('element', ''))
                })
            return json.dumps(formatted, indent=2)
        
        # Default detailed format
        lines = []
        for bounty in bounties:
            lines.append(f"🎯 {bounty.get('index')}. {bounty.get('title', 'Unknown Bounty')}")
            lines.append(f"   Points: {bounty.get('points', 1)} | Difficulty: {bounty.get('difficulty', 'medium')}")
            lines.append(f"   Tags: {', '.join(bounty.get('tags', [])) if bounty.get('tags') else 'N/A'}")
            lines.append(f"   Age: {bounty.get('age_days', 0)} days | Score: {bounty.get('score', 1)}\n")
        
        return '\n'.join(lines)
    
    def _save_results(self, bounties, output_file=None):
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(self._format_output(bounties, 'json'))
            return True
        return True
    
    def _create_summary(self, bounties):
        total = len(bounties)
        avg_score = sum(b.get('score', 1) for b in bounties) / total if total else 1
        top_tags = []
        all_tags = []
        
        for bounty in bounties:
            all_tags.extend(bounty.get('tags', []))
        
        for tag, count in Counter(all_tags):
            if count >= 2 and tag not in top_tags:
                top_tags.append(tag)
        
        summary = f"""Bounty Scout Summary
====================
Total Bounties: {total}
Average Score: {avg_score:.1f}
Top Tags: {', '.join(top_tags[:5]) if top_tags else 'None'}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        return summary
    
    def scout(self, session=None, source='html', output='detailed'):
        if session is None:
            session = self.session
        
        bounties = self._process_bounties(session, source)
        bounties = [self._enrich_bounty(b) for b in bounties]
        bounties = self._filter_bounties(bounties)
        
        if output == 'detailed':
            return self._format_output(bounties)
        
        elif output == 'json':
            return json.dumps([{'title': b.get('title'), 'score': b.get('score'), 'url': b.get('url')} for b in bounties], indent=2)
        
        else:
            return self._format_output(bounties, output)
    
    def discover(self, keywords=None, session=None, source='html'):
        if not keywords:
            keywords = self.config.get('keywords', [])
        
        bounties = self.scout(session=session, source=source)
        final_bounties = [b for b in bounties if any(kw in b.get('title', '').lower() for kw in keywords)]
        return final_bounties


class BountyScoutMain:
    def __init__(self):
        self.scout = BountyScout()
    
    def run(self, *args, **kwargs):
        result = self.scout.scout(*args, **kwargs)
        print(result)
        return result


def main():
    scout = BountyScoutMain()
    
    # Example configuration
    config = {
        'url': 'https://example.com/bounties',
        'limit': 50,
        'source': 'html',
        'filters': {'difficulty': ['easy', 'medium']}
    }
    
    try:
        bounties = scout.scout(config=config, output='detailed')
        print(bounties)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()