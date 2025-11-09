#!/usr/bin/env python
# coding: utf-8

import os
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool
from typing import Optional

import requests


def get_page_count(issue_id: str, date_string: str) -> int:
    """Get total number of pages for given issue and date."""
    url = f"https://www.enewspapr.com/OutSourcingDataChanged.php?operation=getPageArticleDetails&selectedIssueId={issue_id}_{date_string}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error getting page count: {response.status_code}")
        return 0
        
    try:
        page_count = len(response.json())
        return page_count
    except Exception as e:
        print(f"Error parsing page count response: {e}")
        return 0


def download_page(issue_id: str, date_string: str, page_no: int) -> Optional[str]:
    """Download a single page PDF.
    
    Args:
        issue_id: Paper issue ID (e.g., 'KANPRABHA_MN')
        date_string: Date in YYYYMMDD format
        page_no: Page number to download
    
    Returns:
        str: Path to downloaded file, or None if download failed
    """
    issue = issue_id.split("_")[0]
    region = issue_id.split("_")[1]
    yyyy = date_string[:4]
    mm = date_string[4:6]
    dd = date_string[6:8]
    page_no = str(page_no).zfill(2)

    page_url = f"https://www.enewspapr.com/News/{issue}/{region}/{yyyy}/{mm}/{dd}/{date_string}_{page_no}.PDF"
    
    try:
        response = requests.get(page_url)
        print(f"Downloading {page_url}: {response.status_code}")

        if response.status_code == 200:
            filename = page_url.rsplit("/", 1)[-1]
            filepath = os.path.join("tmp", filename)
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filepath
            
    except Exception as e:
        print(f"Error downloading page {page_no}: {e}")
    
    return None


def download_paper(date_string: str, issue_id: str) -> bool:
    """Download all pages for given issue and date.
    
    Args:
        date_string: Date in YYYYMMDD format
        issue_id: Paper issue ID (e.g., 'KANPRABHA_MN')
    
    Returns:
        bool: True if any pages were downloaded successfully
    """
    page_count = get_page_count(issue_id, date_string)
    if not page_count:
        print("No pages found to download")
        return False

    print(f"Downloading {page_count} pages for {issue_id} {date_string}")
    
    pages = list(range(1, page_count + 1))
    
    # Download pages in parallel
    pool = ThreadPool(8)
    func = partial(download_page, issue_id, date_string)
    
    try:
        results = pool.map(func, pages)
    finally:
        pool.close()
        pool.join()
    
    # Filter out failed downloads
    downloaded = [r for r in results if r]
    success = len(downloaded) > 0
    
    print(f"Downloaded {len(downloaded)}/{page_count} pages")
    return success