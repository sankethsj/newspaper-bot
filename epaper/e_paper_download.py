import requests
from lxml import html

E_PAPER_URL = "https://kpepaper.asianetnews.com/"
E_PAPER_DOWNLOAD_URL = "https://kpepaper.asianetnews.com/download/fullpdflink/newspaper/{region_code}/{paper_code}"


def fetch_todays_paper_code(region: str):

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

    return {
        'status': True,
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
