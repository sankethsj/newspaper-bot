import datetime as dt

import epaper
from flask import Blueprint, jsonify, redirect, render_template

views = Blueprint('views', __name__)

region_info = {
    "Mangaluru": "20312",
    "Bengaluru": "12222"
}


@views.route('/', methods=['GET'])
def home():

    regions = ['Mangaluru', 'Bengaluru']
    print("Fetch regions :", regions)

    return render_template("home.html", regions=regions)


@views.route('/<string:region>/<string:date>', methods=['GET'])
def download_paper(region:str, date:str):

    if date == "today":
        date = dt.datetime.now().strftime("%d-%m-%Y")

    try:
        dt.datetime.strptime(date, "%d-%m-%Y")
    except:
        print(f"Wrong date format : {date}")
        return redirect(f'/{region}')

    paper_info = epaper.fetch_todays_paper_code(region)

    if not paper_info['status']:
        return jsonify(paper_info)

    paper_code = paper_info.get('paper_code')

    region_code = region_info.get(region)

    pdf_info = epaper.fetch_e_paper_pdf_link(region_code, paper_code)

    if pdf_info['status']:
        return redirect(pdf_info['pdf_link'])

    return jsonify(pdf_info)
