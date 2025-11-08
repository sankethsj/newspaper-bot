import datetime as dt
import os
import shutil
from multiprocessing.dummy import Pool as ThreadPool
from typing import List, Dict, Optional

import requests
from pypdf import PdfWriter

BASE_URL = "https://epaper.vishwavani.news"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
)


def get_csrf_token(session: requests.Session, url: str = BASE_URL) -> Optional[str]:
    """Perform a GET to the homepage to obtain CSRF cookie value.

    Returns the csrftoken value or None if not present.
    """
    resp = session.get(url)
    cookies = resp.cookies.get_dict()
    token = cookies.get("csrftoken")
    print("CSRF token:", token)
    return token


def fetch_edition_pages(session: requests.Session, date_str: str, sub_edition: int = 2) -> List[Dict]:
    """Fetch edition page metadata for the given date.

    The site expects a POST to /epaper/api/home with form data: date and sub_edition.
    Returns the list of pages (as dicts) on success, otherwise an empty list.
    """
    api = f"{BASE_URL}/epaper/api/home"
    # Ensure we have a csrftoken in cookies (site may rely on it)
    csrf = session.cookies.get("csrftoken") or get_csrf_token(session)

    headers = {
        "User-Agent": USER_AGENT,
        "Referer": BASE_URL + "/",
        "x-csrftoken": csrf or "",
    }

    data = {"date": date_str, "sub_edition": str(sub_edition)}

    resp = session.post(api, headers=headers, data=data)
    if resp.status_code != 200:
        print(f"Failed to fetch edition pages: {resp.status_code} {resp.text}")
        return []

    try:
        j = resp.json()
    except Exception as e:
        print("Failed to parse JSON from edition API:", e)
        return []

    # API response shape expected in comments: {result: true, pages: [...]}
    pages = j.get("pages") if isinstance(j, dict) else None
    if not pages:
        print("No pages found in API response")
        return []
    print(f"Found {len(pages)} pages for date {date_str}")
    return pages


def download_page_pdf(session: requests.Session, page: Dict, out_dir: str = "tmp") -> Optional[str]:
    """Download a single page PDF using page dict from the API.

    The page dict typically contains 'page_id' and/or 'pdf_url'.
    Returns the path to the saved file on success, otherwise None.
    """
    os.makedirs(out_dir, exist_ok=True)

    page_id = page.get("page_id")
    pdf_url = page.get("pdf_url")

    # Prefer the provided pdf_url if available; otherwise use the download endpoint
    if pdf_url:
        download_url = pdf_url
    elif page_id:
        download_url = f"{BASE_URL}/download/{page_id}/pdf"
    else:
        print("No downloadable URL or page_id for page:", page)
        return None

    csrf = session.cookies.get("csrftoken")
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": BASE_URL + "/",
        "x-csrftoken": csrf or "",
    }

    try:
        r = session.get(download_url, headers=headers, stream=True, timeout=30)
    except Exception as e:
        print("Error downloading", download_url, e)
        return None

    if r.status_code != 200:
        print(f"Failed to download {download_url}: {r.status_code}")
        return None

    # derive filename
    filename = None
    if page_id:
        filename = f"{page_id}.pdf"
    else:
        filename = f"page_{page.get('id', 'unknown')}.pdf"

    out_path = os.path.join(out_dir, filename)
    try:
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(1024 * 64):
                if chunk:
                    f.write(chunk)
        print("Downloaded", out_path)
        return out_path
    except Exception as e:
        print("Failed to save file", out_path, e)
        return None


def download_all_pages(session: requests.Session, pages: List[Dict], out_dir: str = "tmp", workers: int = 8) -> List[str]:
    """Download all pages in parallel and return list of saved file paths (order not guaranteed).

    pages should be the list returned by fetch_edition_pages (keeps ordering info inside each dict).
    """
    if not pages:
        return []

    os.makedirs(out_dir, exist_ok=True)
    pool = ThreadPool(workers)
    try:
        results = pool.map(lambda p: download_page_pdf(session, p, out_dir), pages)
    finally:
        pool.close()
        pool.join()

    saved = [r for r in results if r]
    print(f"Downloaded {len(saved)}/{len(pages)} pages")
    return saved


def merge_pdfs(tmp_dir: str, output_path: str) -> bool:
    """Merge all PDFs in tmp_dir into a single PDF at output_path.

    Files will be sorted reasonably by filename. Returns True on success.
    """
    if not os.path.isdir(tmp_dir):
        print("tmp_dir not found:", tmp_dir)
        return False

    files = [f for f in os.listdir(tmp_dir) if f.lower().endswith('.pdf')]
    if not files:
        print("No PDF files found in tmp_dir")
        return False

    # Try to sort by natural numeric order if file names contain page numbers.
    files = sorted(files)

    writer = PdfWriter()
    for fn in files:
        path = os.path.join(tmp_dir, fn)
        try:
            writer.append(path)
            print("Appended", path)
        except Exception as e:
            print("Failed to append", path, e)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        writer.write(output_path)
        writer.close()
        print("Merged PDF saved:", output_path)
        return True
    except Exception as e:
        print("Failed to write merged PDF:", e)
        return False


def cleanup_old_files(output_dir: str = "output", days: int = 7):
    """Delete files in output_dir older than `days` days (based on filename date pattern YYYYMMDD or mtime)."""
    if not os.path.isdir(output_dir):
        return

    now = dt.datetime.now()
    for fn in os.listdir(output_dir):
        path = os.path.join(output_dir, fn)
        # Try to extract date from filename like something_YYYYMMDD.pdf
        date_str = None
        try:
            base = fn.rsplit('_', 1)[-1].split('.', 1)[0]
            if len(base) == 8 and base.isdigit():
                date_str = base
        except Exception:
            date_str = None

        file_dt = None
        if date_str:
            try:
                file_dt = dt.datetime.strptime(date_str, "%Y%m%d")
            except Exception:
                file_dt = None

        # fallback to modification time
        if file_dt is None:
            mtime = dt.datetime.fromtimestamp(os.path.getmtime(path))
            file_dt = mtime

        if (now - file_dt).days > days:
            try:
                os.remove(path)
                print("Deleted old file:", path)
            except Exception as e:
                print("Failed to delete", path, e)


def run_for_date(date_str: Optional[str] = None, sub_edition: int = 2):
    """High-level runner: fetch pages for date, download, merge into output, cleanup tmp.

    date_str: YYYY-MM-DD or YYYYMMDD. If None, uses today's India date.
    """
    # normalize date string to YYYY-MM-DD for API (sample used 2025-11-07 format)
    if not date_str:
        now = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)
        date_str = now.strftime("%Y-%m-%d")
    else:
        # allow YYYYMMDD -> YYYY-MM-DD
        if len(date_str) == 8 and date_str.isdigit():
            date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    session = requests.Session()
    get_csrf_token(session)

    pages = fetch_edition_pages(session, date_str, sub_edition=sub_edition)
    if not pages:
        print("No pages to download; exiting")
        return

    tmp_dir = "tmp"
    saved_files = download_all_pages(session, pages, out_dir=tmp_dir, workers=8)
    print(f"Downloaded {len(saved_files)} files to {tmp_dir}")

    # derive output filename in bot.py style: ISSUEID_REGION_YYYYMMDD.pdf is not known here,
    # so use publisher + date filename.
    out_dir = "output"
    os.makedirs(out_dir, exist_ok=True)
    out_date_compact = date_str.replace('-', '')
    output_path = os.path.join(out_dir, f"VISHWAVANI_{sub_edition}_{out_date_compact}.pdf")

    merged = merge_pdfs(tmp_dir, output_path)

    # cleanup tmp
    try:
        shutil.rmtree(tmp_dir)
    except Exception:
        pass

    if merged:
        print("Paper saved to", output_path)
    else:
        print("Paper could not be merged")

    # delete files older than 7 days
    cleanup_old_files(out_dir, days=7)


if __name__ == "__main__":
    
    current_time = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)
    print("Current India time :", current_time)

    date_str = current_time.strftime("%Y-%m-%d")
    print("Using date:", date_str)

    run_for_date(date_str, sub_edition=2)
