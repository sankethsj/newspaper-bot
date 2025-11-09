#!/usr/bin/env python
# coding: utf-8

import os
from multiprocessing.dummy import Pool as ThreadPool
from typing import Optional
import requests
from bs4 import BeautifulSoup
import re

# User agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_page_urls(date_string: str, edition: str = "2") -> list:
    """Get all page image URLs for given date.

    Args:
        date_string: Date in DD-MMM-YYYY format (e.g., '09-Nov-2025')
        edition: Edition number (default '2' for Mangaluru)

    Returns:
        list: List of full-resolution image URLs
    """
    base_url = "https://epaper.hosadigantha.com"
    page_url = f"{base_url}/epaper/go/{date_string}/{edition}"

    try:
        # Get the HTML page with redirect handling
        session = requests.Session()
        response = session.get(page_url, headers=HEADERS, allow_redirects=True)
        if response.status_code != 200:
            print(f"Error getting page: {response.status_code}")
            return []

        # Print the final URL after redirect
        print(f"Redirected to: {response.url}")

        # Parse HTML to find image URLs
        soup = BeautifulSoup(response.text, "html.parser")
        thumb_bar = soup.find("div", class_="rthumb_bar")
        if not thumb_bar:
            print("Could not find thumbnail bar")
            return []

        image_urls = []
        for thumb in thumb_bar.find_all("a"):
            img_tag = thumb.find("img")
            if img_tag and "src" in img_tag.attrs:
                # Get the thumbnail URL and remove width/height parameters
                thumb_url = img_tag["src"]
                # Remove width and height parameters to get full resolution
                thumb_url = re.sub(r"&width=\d+", "", thumb_url)
                thumb_url = re.sub(r"&height=\d+", "", thumb_url)
                image_urls.append(thumb_url)

        return image_urls

    except Exception as e:
        print(f"Error parsing page URLs: {e}")
        return []


def download_page(url: str, page_no: int, output_dir: str = "tmp") -> Optional[str]:
    """Download a single page image and convert to PDF.

    Args:
        url: Full resolution image URL
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
        img_path = os.path.join(output_dir, f"page_{page_no}.jpg")
        with open(img_path, "wb") as f:
            f.write(response.content)

        # Convert image to PDF (using the same filename pattern as Kannada Prabha)
        # TODO: Add image to PDF conversion here using img2pdf
        # For now, we'll just return the image path
        return img_path

    except Exception as e:
        print(f"Error downloading page {page_no}: {e}")
        return None


def download_paper(date_string: str, edition: str = "2") -> bool:
    """Download all pages for given date.

    Args:
        date_string: Date in DD-MMM-YYYY format (e.g., '09-Nov-2025')
        edition: Edition number (default '2' for Mangaluru)

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
