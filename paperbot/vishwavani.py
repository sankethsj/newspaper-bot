#!/usr/bin/env python
# coding: utf-8

import os
from multiprocessing.dummy import Pool as ThreadPool
from typing import Dict, List, Optional

import requests

BASE_URL = "https://epaper.vishwavani.news"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
)


def get_csrf_token(session: requests.Session) -> Optional[str]:
    """Get CSRF token from homepage."""
    try:
        resp = session.get(BASE_URL)
        return resp.cookies.get("csrftoken")
    except Exception as e:
        print(f"Error getting CSRF token: {e}")
        return None


def fetch_edition_pages(session: requests.Session, date_str: str, sub_edition: int = 2) -> List[Dict]:
    """Fetch page metadata for the edition."""
    csrf = session.cookies.get("csrftoken") or get_csrf_token(session)
    if not csrf:
        print("Failed to get CSRF token")
        return []

    headers = {
        "User-Agent": USER_AGENT,
        "Referer": BASE_URL + "/",
        "x-csrftoken": csrf,
    }

    # API expects YYYY-MM-DD format
    if len(date_str) == 8:  # YYYYMMDD
        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    try:
        resp = session.post(
            f"{BASE_URL}/epaper/api/home",
            headers=headers,
            data={"date": date_str, "sub_edition": str(sub_edition)}
        )

        if resp.status_code != 200:
            print(f"API error: {resp.status_code}")
            return []

        data = resp.json()
        pages = data.get("pages", []) if isinstance(data, dict) else []
        
        if not pages:
            print("No pages found in API response")
        else:
            print(f"Found {len(pages)} pages")
            
        return pages

    except Exception as e:
        print(f"Error fetching edition pages: {e}")
        return []


def download_page(session: requests.Session, page: Dict) -> Optional[str]:
    """Download a single page PDF."""
    page_id = page.get("page_id")
    if not page_id:
        return None

    csrf = session.cookies.get("csrftoken")
    if not csrf:
        print("No CSRF token available")
        return None

    headers = {
        "User-Agent": USER_AGENT,
        "Referer": BASE_URL + "/",
        "x-csrftoken": csrf,
    }

    download_url = f"{BASE_URL}/download/{page_id}/pdf"
    
    try:
        r = session.get(download_url, headers=headers, stream=True, timeout=30)
        if r.status_code != 200:
            print(f"Download failed: {r.status_code}")
            return None

        filename = f"{page_id}.pdf"
        filepath = os.path.join("tmp", filename)
        
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(1024 * 64):
                if chunk:
                    f.write(chunk)
        
        print(f"Downloaded page {page_id}")
        return filepath

    except Exception as e:
        print(f"Error downloading page {page_id}: {e}")
        return None


def download_paper(date_string: str, sub_edition: int = 2) -> bool:
    """Download complete paper for date.
    
    Args:
        date_string: Date in YYYYMMDD format
        sub_edition: Sub-edition number (default 2)
    
    Returns:
        bool: True if any pages were downloaded successfully
    """
    session = requests.Session()
    if not get_csrf_token(session):
        print("Failed to initialize session")
        return False

    pages = fetch_edition_pages(session, date_string, sub_edition)
    if not pages:
        return False

    # Download pages in parallel
    pool = ThreadPool(8)
    try:
        results = pool.map(lambda p: download_page(session, p), pages)
    finally:
        pool.close()
        pool.join()

    # Filter out failed downloads
    downloaded = [r for r in results if r]
    success = len(downloaded) > 0
    
    print(f"Downloaded {len(downloaded)}/{len(pages)} pages")
    return success