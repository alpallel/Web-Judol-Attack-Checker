#!/usr/bin/env python3
"""
check_judol.py

Usage:
  python check_judol.py --sitemap sitemap.xml

This script parses a sitemap.xml, fetches each URL concurrently, and checks
whether the page content contains the string "judol" (case-insensitive).
It writes a JSON report (default: judol_report.json) and prints a short summary.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import xml.etree.ElementTree as ET

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("Missing required dependency 'requests'.\nInstall it with:\n  pip install -r requirements.txt\nor\n  python -m pip install requests", file=sys.stderr)
    raise


def parse_sitemap(path: str) -> List[str]:
    """Return list of URLs found in <loc> elements of sitemap.xml."""
    tree = ET.parse(path)
    root = tree.getroot()
    # handle namespace if present
    ns = ''
    if root.tag.startswith('{'):
        ns = root.tag.split('}')[0].strip('{')
    if ns:
        locs = root.findall('.//{{{}}}loc'.format(ns))
    else:
        locs = root.findall('.//loc')
    urls = [e.text.strip() for e in locs if e is not None and e.text]
    return urls


def make_session(retries: int = 3, backoff: float = 0.3, timeout: int = 10) -> requests.Session:
    s = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff, status_forcelist=(500, 502, 503, 504))
    adapter = HTTPAdapter(max_retries=retry)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    s.headers.update({'User-Agent': 'judol-checker/1.0'})
    return s


def fetch_url(session: requests.Session, url: str, timeout: int = 10) -> Dict:
    try:
        r = session.get(url, timeout=timeout)
        text = r.text or ''
        text_lower = text.lower()
        has_judol = any(keyword in text_lower for keyword in ('judol', 'gacor', 'togel', 'maxwin'))
        exact_judol = text.strip().lower() == 'judol'
        return { 
            'url': url,
            'ok': True,
            'status_code': r.status_code,
            'has_judol': has_judol,
            'exact_judol': exact_judol,
            'length': len(text),
        }
    except Exception as e:
        return {'url': url, 'ok': False, 'error': str(e)}


def run_checker(sitemap: str, output: str, concurrency: int, timeout: int) -> Dict:
    urls = parse_sitemap(sitemap)
    session = make_session()
    results = []
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(fetch_url, session, u, timeout): u for u in urls}
        for f in as_completed(futures):
            results.append(f.result())
    session.close()

    report = {'sitemap': sitemap, 'count': len(urls), 'results': results}
    with open(output, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    return report


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Check sitemap pages for the string "judol"')
    parser.add_argument('--sitemap', '-s', default='sitemap.xml', help='Path to sitemap.xml')
    parser.add_argument('--output', '-o', default='judol_report.json', help='Output JSON report file')
    parser.add_argument('--concurrency', '-c', type=int, default=10, help='Number of concurrent requests')
    parser.add_argument('--timeout', '-t', type=int, default=10, help='Request timeout in seconds')
    args = parser.parse_args(argv)

    try:
        report = run_checker(args.sitemap, args.output, args.concurrency, args.timeout)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 2

    total = report['count']
    found = [r for r in report['results'] if r.get('has_judol')]
    exact = [r for r in report['results'] if r.get('exact_judol')]

    print(f'Sitemap: {args.sitemap}  URLs checked: {total}')
    print(f'Pages containing "judol": {len(found)}')
    if found:
        print('\nMatches:')
        for r in found:
            print(f" - {r['url']} (status={r.get('status_code')})")
    if exact:
        print('\nExact-body == "judol" (likely defacement):')
        for r in exact:
            print(f" - {r['url']}")

    print(f'Full report written to: {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
