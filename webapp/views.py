from flask import Blueprint, render_template, redirect, jsonify

import epaper

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def home():

    regions = epaper.fetch_available_regions()
    print("Fetch regions :", regions)

    return render_template("home.html", regions=regions)

@views.route('/<string:region>', methods=['GET'])
def region_papers(region:str):

    region_info = epaper.fetch_region_info(region)

    return render_template("region.html", region=region, region_info=region_info)


@views.route('/<string:region>/<string:date>', methods=['GET'])
def download_paper(region:str, date:str):

    region_info = epaper.fetch_region_info(region)
    region_code = region_info.get('region_code')

    paper_info = epaper.fetch_e_paper_code(region)
    paper_code = paper_info.get('paper_code')

    pdf_info = epaper.fetch_e_paper_pdf_link(region_code, paper_code)

    if pdf_info['status']:
        return redirect(pdf_info['pdf_link'])

    return jsonify(pdf_info)
