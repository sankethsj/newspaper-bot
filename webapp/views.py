import datetime as dt
import requests
from flask import Blueprint, redirect, render_template

views = Blueprint("views", __name__)


def get_papers_list():
    URL = "https://api.github.com/repos/sankethsj/newspaper-bot/contents/output"
    response = requests.get(URL)

    papers = []
    if response.status_code == 200:
        papers = response.json()

    return papers


@views.route("/", methods=["GET"])
def home():
    # papers = get_papers_list()

    # if papers:
    #     papers = sorted(papers, key=lambda x: x["path"], reverse=True)

    # for paper in papers:
    #     paper["title"] = "Kannada Prabha"
    #     paper["region"] = "Mangaluru"
    #     # sample paper name : KANPRABHA_MN_20240120.pdf
    #     date_string = paper["name"].split(".")[0].split("_")[-1]
    #     paper["date"] = dt.datetime.strptime(date_string, "%Y%m%d").strftime("%d-%m-%Y")
    #     paper["size"] = round(paper["size"] / 1000000, 2)

    return render_template("home.html", papers=[])


@views.route("/download/<string:sha>", methods=["GET"])
def download_paper(sha: str):
    papers = get_papers_list()

    for paper in papers:
        if paper["sha"] == sha:
            return redirect(paper["download_url"])

    return render_template("download_error.html")
