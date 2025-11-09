#!/usr/bin/env python
# coding: utf-8

import datetime as dt
import os
import shutil
from typing import Optional

import img2pdf
from pypdf import PdfWriter


def get_india_time() -> dt.datetime:
    """Get current time in India (UTC+5:30)."""
    return dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)


def get_date_string(date: Optional[dt.datetime] = None, format: str = "%Y%m%d") -> str:
    """Get formatted date string. Uses current India time if date not provided."""
    if date is None:
        date = get_india_time()
    return dt.datetime.strftime(date, format)


def merge_pdfs(tmp_dir: str, output_path: str) -> bool:
    """Merge all PDFs or images in tmp_dir into a single PDF at output_path.
    
    Args:
        tmp_dir: Directory containing PDF/JPG files to merge
        output_path: Path where merged PDF should be saved
    
    Returns:
        bool: True if merge was successful
    """
    if not os.path.isdir(tmp_dir):
        print("tmp_dir not found:", tmp_dir)
        return False

    # Check for both PDF and JPG files
    pdf_files = [f for f in os.listdir(tmp_dir) if f.lower().endswith('.pdf')]
    jpg_files = [f for f in os.listdir(tmp_dir) if f.lower().endswith('.jpg')]

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if jpg_files:
        # Handle image files using img2pdf
        print("Found JPG files, converting to PDF...")
        jpg_files = sorted(jpg_files)  # Sort to maintain page order
        image_paths = [os.path.join(tmp_dir, f) for f in jpg_files]
        
        try:
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(image_paths))
            print("E-paper saved:", output_path)
            return True
        except Exception as e:
            print(f"Error converting images to PDF: {e}")
            return False

    elif pdf_files:
        # Handle PDF files using PdfWriter
        print("Found PDF files, merging...")
        pdf_files = sorted(pdf_files)
        merger = PdfWriter()
        
        try:
            for pdf in pdf_files:
                merger.append(os.path.join(tmp_dir, pdf))
                
            merger.write(output_path)
            merger.close()
            print("E-paper saved:", output_path)
            return True
        except Exception as e:
            print(f"Error merging PDFs: {e}")
            merger.close()
            return False
    else:
        print("No PDF or JPG files found in tmp_dir")
        return False


def cleanup_old_files(output_dir: str = "output", days: int = 7) -> None:
    """Delete files in output_dir older than specified days."""
    if not os.path.isdir(output_dir):
        return

    current_time = get_india_time()
    
    for file in os.listdir(output_dir):
        try:
            file_date_str = file.split("_")[-1].split(".")[0]
            file_date = dt.datetime.strptime(file_date_str, "%Y%m%d")
            
            if (current_time.replace(tzinfo=None) - file_date).days > days:
                file_path = os.path.join(output_dir, file)
                print(f"Deleting file '{file}' older than {days} days")
                os.remove(file_path)
        except (IndexError, ValueError) as e:
            print(f"Skipping file '{file}': {str(e)}")


def cleanup_temp_dir(tmp_dir: str = "tmp") -> None:
    """Clean up temporary directory."""
    try:
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
            print(f"Cleaned up '{tmp_dir}' directory")
    except Exception as e:
        print(f"Error cleaning up '{tmp_dir}': {e}")


def ensure_dirs_exist(*dirs: str) -> None:
    """Ensure all specified directories exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)