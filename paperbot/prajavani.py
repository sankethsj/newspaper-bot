#!/usr/bin/env python
# coding: utf-8
import os
from multiprocessing.dummy import Pool as ThreadPool
from typing import Optional

import requests

# User agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_page_urls(date_string: str, edition: str = "4") -> list:
    """Get all page image URLs for given date.

    Args:
        date_string: Date in YYYYMMDD format (e.g., '20260506')
        edition: Edition number (default '4' for Bengaluru)

    Returns:
        list: List of full-resolution pdf URLs
    """
    base_url = "https://api-epaper-prod.deccanherald.com"
    data_url = (
        f"{base_url}/epaper/data?date={date_string}&edition={edition}&publisher=PV"
    )

    try:
        # Get the HTML page with redirect handling
        session = requests.Session()
        response = session.get(data_url, headers=HEADERS, allow_redirects=True)
        if response.status_code != 200:
            print(f"Error getting page: {response.status_code}")
            print(f"Error: {response.text}")
            return []

        # Print the final URL after redirect
        print(f"Redirected to: {response.url}")

        page_data = response.json()

        page_url_format = "https://assets-prod.prajavani.net/PV/{date_string}/data/webepaper/pdf/{page_id}.pdf"

        pages = page_data.get("data", {}).get("sections", [{}])[0].get("pages", [])
        std_pages = [
            {"page_no": page.get("absPageNo", 0), "page_id": page.get("id")}
            for page in pages
            if page.get("sectionName", "").lower() == "std"
        ]
        sorted_std_pages = sorted(std_pages, key=lambda x: x["page_no"])

        pdf_urls = [
            page_url_format.format(date_string=date_string, page_id=item.get("page_id"))
            for item in sorted_std_pages
        ]

        return pdf_urls

    except Exception as e:
        print(f"Error parsing page URLs: {e}")
        return []


def download_page(url: str, page_no: int, output_dir: str = "tmp") -> Optional[str]:
    """Download a single page pdf.

    Args:
        url: Full resolution pdf URL
        page_no: Page number (for filename)
        output_dir: Directory to save files (default 'tmp')

    Returns:
        str: Path to downloaded PDF file, or None if download failed
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Download image
        print(f"Downloading {url}")
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error downloading page {page_no}: {response.status_code}")
            return None

        # Save as temporary image file
        pdf_path = os.path.join(output_dir, f"page_{page_no}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(response.content)

        return pdf_path

    except Exception as e:
        print(f"Error downloading page {page_no}: {e}")
        return None


def download_paper(date_string: str, edition: str = "4") -> bool:
    """Download all pages for given date.

    Args:
        date_string: Date in YYYYMMDD format (e.g., '20260506')
        edition: Edition number (default '4' for Bengaluru)

    Returns:
        bool: True if any pages were downloaded successfully
    """
    # Get all page URLs
    page_urls = get_page_urls(date_string, edition)
    if not page_urls:
        print("No pages found to download")
        return False

    print(f"Found {len(page_urls)} pages to download")

    # Download pages in parallel
    pool = ThreadPool(8)

    try:
        # Create list of (url, page_no) tuples for downloading
        download_tasks = [(url, idx, "tmp") for idx, url in enumerate(page_urls, 1)]
        results = pool.starmap(download_page, download_tasks)
    finally:
        pool.close()
        pool.join()

    # Filter out failed downloads
    downloaded = [r for r in results if r]
    success = len(downloaded) > 0

    print(f"Downloaded {len(downloaded)}/{len(page_urls)} pages")
    return success
