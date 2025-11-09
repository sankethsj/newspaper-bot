#!/usr/bin/env python
# coding: utf-8

import os
from typing import Dict, Optional

from datetime import datetime
from paperbot.utils import (
    cleanup_old_files,
    cleanup_temp_dir,
    ensure_dirs_exist,
    get_date_string,
    get_india_time,
    merge_pdfs,
)
from paperbot import kannada_prabha, vishwavani, hosadigantha


def process_paper(
    name: str, date_string: str, download_func: callable, **kwargs
) -> Optional[str]:
    """Process (download and merge) a single paper.

    Args:
        name: Paper name (used in output filename)
        date_string: Date in YYYYMMDD format
        download_func: Function to call to download paper
        **kwargs: Additional arguments for download_func

    Returns:
        str: Path to merged PDF if successful, None otherwise
    """
    ensure_dirs_exist("tmp", "output")

    print(f"\nProcessing {name} for date {date_string}")

    try:
        if not download_func(date_string, **kwargs):
            print(f"Failed to download {name}")
            return None

        if "-" in date_string:
            # Convert DD-MMM-YYYY to YYYYMMDD format
            date_string = datetime.strptime(date_string, "%d-%b-%Y").strftime("%Y%m%d")
        
        output_path = os.path.join("output", f"{name}_{date_string}.pdf")
        if merge_pdfs("tmp", output_path):
            return output_path

    except Exception as e:
        print(f"Error processing {name}: {e}")

    finally:
        cleanup_temp_dir()

    return None


def check_existing(date_string: str, paper_id: str) -> bool:
    """Check if paper already exists for date."""
    if not os.path.exists("output"):
        return False

    for file in os.listdir("output"):
        if file.startswith(paper_id) and date_string in file:
            print(f"Paper {paper_id} for date {date_string} already exists")
            return True
    return False


def process_all_papers() -> Dict[str, Optional[str]]:
    """Process all configured papers for today's date.

    Returns:
        Dict mapping paper names to output paths (or None if failed)
    """
    current_time = get_india_time()
    print("Current India time:", current_time)

    date_string = get_date_string(current_time)
    results = {}

    # Kannada Prabha
    paper_id = "KANPRABHA_MN"
    if not check_existing(date_string, paper_id):
        results[paper_id] = process_paper(
            paper_id, date_string, kannada_prabha.download_paper, issue_id=paper_id
        )

    # Vishwavani (both editions if needed)
    for edition in [2]:  # Add more editions if needed
        paper_id = f"VISHWAVANI_{edition}"
        if not check_existing(date_string, paper_id):
            results[paper_id] = process_paper(
                paper_id, date_string, vishwavani.download_paper, sub_edition=edition
            )

    # Hosa Digantha
    paper_id = "HOSADIGANTHA_MN"
    if not check_existing(date_string, paper_id):
        # Convert YYYYMMDD to DD-MMM-YYYY format for Hosa Digantha
        hd_date = datetime.strptime(date_string, "%Y%m%d").strftime("%d-%b-%Y")
        results[paper_id] = process_paper(
            paper_id,
            hd_date,
            hosadigantha.download_paper,
            edition="2",  # edition 2 for Mangaluru
        )

    return results


if __name__ == "__main__":
    ensure_dirs_exist("tmp", "output")

    results = process_all_papers()

    # Report results
    print("\nProcessing complete:")
    for paper, path in results.items():
        if path:
            print(f"✓ {paper}: {path}")
        else:
            print(f"✗ {paper}: Failed to process")

    # Cleanup old files
    cleanup_old_files(days=7)
    cleanup_temp_dir()
