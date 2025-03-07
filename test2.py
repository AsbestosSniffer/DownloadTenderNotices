import os
import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = 'http://www.ha.org.hk/visitor/ha_view_content.asp?content_id=276313&lang=ENG'  # Replace with the actual URL
download_folder = os.path.join(os.getcwd(), 'test2') # Append folder name to current working directory

# Ensure the download folder exists
os.makedirs(download_folder, exist_ok=True)

# Function to download PDFs
def download_pdf(pdf_url, pdf_name):
    print(f'Downloading: {pdf_url}')
    # Fetch the PDF
    pdf_response = requests.get(url, allow_redirects=True)
    pdf_name = pdf_name.translate(str.maketrans('', '', "!@#$()-/\\")) + '.pdf' # Remove chars not allowed in PDF file name
    pdf_path = os.path.join(download_folder, pdf_name) # Path of PDF file
    with open(pdf_path, 'wb') as f:
        f.write(pdf_response.content)
    print(f'Downloaded: {pdf_name}')
    
download_pdf(url, "testpdf")



