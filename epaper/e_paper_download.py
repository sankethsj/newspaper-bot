import datetime as dt

import requests
from lxml import html

from .region_data import Region


E_PAPER_URL = "https://kpepaper.asianetnews.com/"
E_PAPER_DOWNLOAD_URL = "https://kpepaper.asianetnews.com/download/fullpdflink/newspaper/{region_code}/{paper_code}"


regions_data = Region()

def fetch_available_regions():

    return regions_data.get_availabe_regions()


def fetch_region_info(region):

    return regions_data.get_region_info(region)


def fetch_e_paper_code(region, date:str = None):

    region_code = regions_data.get_region_code(region)

    if region_code is None:
        return {
            'status': False,
            'message': f"Region '{region}' is not supported"
        }

    if date is None:
        todays_date = dt.datetime.now().strftime("%d-%m-%Y")
    else:
        todays_date = date

    paper_code = regions_data.get_paper_code(region, todays_date)

    if paper_code is None:
        # ping homepage to get paper codes
        response = requests.get(E_PAPER_URL)

        tree = html.fromstring(response.text)

        # xpath to find region specific header tags
        header_element = tree.xpath(f'//h3[contains(text(),"{region}")]')[0]

        if header_element is None:
            error_msg = f"Invalid region : {region} not found"
            return {
                'status': False,
                'message': error_msg
            }

        # parent of header tag contains link to e-paper
        link_to_paper = header_element.getparent().getparent().get('href')
        paper_code = link_to_paper.split("/")[-1]

        regions_data.set_region_info(region, paper_code)

    return {
        'status': True,
        'region_code': region_code,
        'paper_code': paper_code
    }


def fetch_e_paper_pdf_link(region_code, paper_code):

    pdf_url = E_PAPER_DOWNLOAD_URL.format(
        region_code=region_code, 
        paper_code=paper_code
    )

    response = requests.get(pdf_url)
    data = response.json()

    if data['status']:

        return {
            'status': True,
            'pdf_link': data['data']['fullpdf']
        }
    
    return data
