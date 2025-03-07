import os
import requests
from bs4 import BeautifulSoup


# URL of the page to scrape
url = 'https://www.ha.org.hk/haho/ho/bssd/TN_257201_00034245a.htm'  # Replace with the actual URL
download_folder = os.path.join(os.getcwd(), 'test') # Append folder name to current working directory

# Function to download PDFs
def download_pdf(pdf_url, pdf_name):
    print(f'Downloading: {pdf_url}')
    response = requests.get(pdf_url)
    if response.status_code == 200:
        pdf_name = pdf_name.translate(str.maketrans('', '', "!@#$()-/\\")) + '.pdf' # Remove chars not allowed in PDF file name
        pdf_path = os.path.join(download_folder, pdf_name) # Path of PDF file
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        print(f'Downloaded: {pdf_name}')
    else:
        print(f"Failed to download {pdf_name}")
    
# Fetch the page
response = requests.get(url)
html_content = response.text

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table with the tender invitations
table = soup.find('table')

# Extract the links from the table
for row in table.find_all('tr')[1:]:  # Skip the header row
    cols = row.find_all('td')
    if len(cols) > 1:
        # Get the reference of the tender notice
        tender_ref = cols[0].find('p').getText()
        print(tender_ref)
        # Get the link to the webpage of the tender notice
        tender_link_tag = cols[1].find('a') # Get the link tag ('<a>') from the second column
        tender_link = tender_link_tag['href'] # Get link from the link tag
        tender_name = tender_link_tag.getText() # Get name from the link tag
        print(tender_link)
        print(tender_name)

        # Get the webpage of the tender notice
        tender_response = requests.get(tender_link)
        tender_soup = BeautifulSoup(tender_response.text, 'html.parser')

        # Find the PDF link in the tender document page
        pdf_url = tender_soup.find('a')['href']

        pdf_response_html = requests.get(pdf_url, allow_redirects=True)
        pdf_response_script_tag = pdf_response_html.find('body').descendants.find('script')
        print(pdf_response_script_tag.getText())
        
        
