from webapp import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


# import epaper

# region = 'Belagavi'

# response = epaper.fetch_e_paper_code(region)
# print("Fetch e-paper code :",response)

# if response['status']:

#     region_code = response['region_code']
#     paper_code = response['paper_code']

#     response = epaper.fetch_e_paper_pdf_link(region_code, paper_code)

#     print("Fetch pdf link :", response)
