#!/usr/bin/env python
# coding: utf-8

import datetime as dt
import os
import shutil
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool

import requests
from PyPDF2 import PdfWriter


def get_page_count(issue_id, date_string):
    url = f"https://www.enewspapr.com/OutSourcingDataChanged.php?operation=getPageArticleDetails&selectedIssueId={issue_id}_{date_string}"
    response = requests.get(url)
    response.status_code
    page_count = len(response.json())
    return page_count


def download_pdf(issue_id, date_string, page_no):

    issue = issue_id.split("_")[0]
    region = issue_id.split("_")[1]
    yyyy = date_string[:4]
    mm = date_string[4:6]
    dd = date_string[6:8]
    page_no = str(page_no).zfill(2)
    
    page_url = f"https://www.enewspapr.com/News/{issue}/{region}/{yyyy}/{mm}/{dd}/{date_string}_{page_no}.PDF"

    response = requests.get(page_url)

    print(page_url, response.status_code)

    if response.status_code == 200:
        filename = page_url.rsplit("/", 1)[-1]
        with open("tmp/" + filename, 'wb') as f:
            f.write(response.content)
    else:
        print("Error :", response.text)


def export_to_single_df(issue_id, date_string):
    
    merger = PdfWriter()
    
    for pdf in os.listdir("tmp"):
        merger.append("tmp/" + pdf)

    out_filename = f"output/{issue_id}_{date_string}.pdf"
    merger.write(out_filename)
    merger.close()
    print("E-paper saved :", out_filename)


if __name__ == "__main__":

    date_string = dt.datetime.strftime(dt.datetime.now(), "%Y%m%d")
    ISSUE_ID = "KANPRABHA_MN"

    print(f"Downloading '{ISSUE_ID}' of date : {date_string}")

    page_count = get_page_count(ISSUE_ID, date_string)
    print("No. of pages :",page_count)

    os.makedirs("tmp", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    pages = []
    for i in range(1, page_count+1):
        pages.append(i)

    print("Downloading all pages...")
    # Make the Pool of workers
    pool = ThreadPool(8)

    func = partial(download_pdf, ISSUE_ID, date_string)
    pool.map(func, pages)
    pool.close()
    pool.join()

    print("Download complete")

    export_to_single_df(ISSUE_ID, date_string)

    print("Cleaning 'tmp' folder")
    shutil.rmtree("tmp")
    print("Complete")