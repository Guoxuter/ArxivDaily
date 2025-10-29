import logging
from typing import List, Dict, Any
import feedparser
import requests
from datetime import datetime, timezone

now_utc = datetime.now(timezone.utc)
import json

logging.getLogger(__name__)

def arxiv_query(query: str, start: int = 0, max_results: int = 300) -> List[Dict[str, Any]]:
    base = 'http://export.arxiv.org/api/query'
    params = {
        'search_query': query,
        'start': start,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    resp = requests.get(base, params=params, timeout=100)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    results = []
    for entry in feed.entries:
        pdf_link = None
        for link in entry.get('links', []):
            if link.get('type') == 'application/pdf' or link.get('title', '').lower() == 'pdf':
                pdf_link = link.get('href')
                break
        if not pdf_link:
            paper_id = entry.get('id', '')
            if paper_id:
                pdf_link = paper_id.replace('/abs/', '/pdf/')
        authors = [a.name for a in entry.get('authors', [])] if entry.get('authors') else []
        categories = [t['term'] for t in entry.tags] if 'tags' in entry else []
        results.append({
            'id': entry.get('id'),
            'title': entry.get('title'),
            'summary': entry.get('summary'),
            'authors': authors,
            'categories': categories,
            'published': entry.get('published'),
            'pdf_url': pdf_link,
            'raw': entry
        })
               

    return results


if __name__ == '__main__':
    query = 'cat:cs.AI OR cat:stat.ML'
    papers = arxiv_query(query)
    for paper in papers:
        print(paper)