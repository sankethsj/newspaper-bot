import datetime as dt

import epaper
from flask import Blueprint, jsonify, redirect, render_template

from .models import Paper, db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def home():

    regions = db.session.query(Paper.region).distinct().all()
    regions = [region[0] for region in regions]
    print("Fetch regions :", regions)

    return render_template("home.html", regions=regions)


@views.route('/<string:region>', methods=['GET'])
def region_papers(region:str):

    region = region.capitalize()

    region_info = Paper.query.filter_by(region=region).order_by(Paper.date.desc()).all()

    print("Region info :", region_info)

    return render_template("region.html", region=region, region_info=region_info)


@views.route('/<string:region>/<string:date>', methods=['GET'])
def download_paper(region:str, date:str):

    if date == "today":
        date = dt.datetime.now().strftime("%d-%m-%Y")

    try:
        dt.datetime.strptime(date, "%d-%m-%Y")
    except:
        print(f"Wrong date format : {date}")
        return redirect(f'/{region}')

    region_info = Paper.query.filter_by(region=region).first()
    print("Region info :", region_info)
    if not region_info:
        return jsonify(status='error', message=f'{region} not supported')

    region_code = region_info.region_code

    paper_info = Paper.query.filter_by(region=region, date=date).first()
    print("Paper info :", paper_info)

    if not paper_info:
        print(f"{region} region Paper code not found for date : {date}")
        paper_info = epaper.fetch_todays_paper_code(region)

        if not paper_info['status']:
            return jsonify(paper_info)

        paper_code = paper_info.get('paper_code')

        paper = Paper(
            region=region, 
            region_code=region_code, 
            date=date, 
            paper_code=paper_code
        )

        db.session.add(paper)
        db.session.commit()
        print("Inserted new record to db :", region, date)

    else:
        paper_code = paper_info.paper_code

    pdf_info = epaper.fetch_e_paper_pdf_link(region_code, paper_code)

    if pdf_info['status']:
        return redirect(pdf_info['pdf_link'])

    return jsonify(pdf_info)
