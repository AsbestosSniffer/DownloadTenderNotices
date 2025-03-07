import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import date
from win32com.client import Dispatch
from eldar import Query
# from openpyxl import Workbook
# from openpyxl.styles import Hyperlink
# from openpyxl.utils import get_column_letter
import pandas as pd
import csv

# filters = ['"Haemoadsorption" OR "hemoadsorption"', '"IVIG" OR "Intravenous immunoglobulin"', 'Albumin', 'Factor VIII', 'Factor IX', 'CMV', 'Wound', 'Dressing', '"Fibroscan" OR "transient elastography"', '"Custodiol" or "HTK Solution"', 'Cardioplegia', 'Transperineal', 'Transplantation', 'Fosfomycin', 'Dapoxetine', 'Perampanel', 'Alprostadil', 'Ropivacaine', 'Propiverine hydrochloride', 'Ganciclovir', 'Valgancicolovir', 'Valaciclovir', 'Letermovir', 'Foscarnet', 'Maribavir', '"Hydrochloride" OR "Endoscopic"']

filters = []
headers = ["ID", "Name", "Link", "Date Downloaded", "Closing Date", "Hospital", "Filters Matched"]

today = date.today()
current_month = today.strftime("%b")
current_year = today.strftime("%Y")

start_url = "https://www.ha.org.hk/visitor/ha_browse_act.asp?Content_ID=2001&Parent_ID=&lang=ENG&Ver=HTML"
year_folder = os.path.join(os.getcwd(), current_year)
month_folder = os.path.join(year_folder, current_month)
shortcuts_folder = os.path.join(year_folder, "shortcuts")
download_folder = month_folder

# Make main storage folders
os.makedirs(year_folder, exist_ok=True)
os.makedirs(month_folder, exist_ok=True)

# Create shortcut folder
os.makedirs(shortcuts_folder, exist_ok=True)

# Path to csv file to store mapping 
database = os.path.join(year_folder, "database.xlsx")

# array of mappings
mappings = []

# array of IDs
IDarray = []

def write_to_excel_pd(data):
    df = pd.DataFrame(data)
    try:
        with pd.ExcelWriter(database, mode='a') as writer: 
            df.to_excel(writer)
        print(f"{current_year} database.xlsx file updated: {df.size} new rows added")
    except FileNotFoundError:
        df.to_excel(database, header=headers)
        print(f"{current_year} database.xlsx file created with {df.size} rows")
    except Exception as e:
        print(f"Something went wrong when creating/updating database.xlsx for {current_year}: {e}")


# def write_to_excel(data, filename):
#     wb = Workbook()
#     ws = wb.active
#     ws.title = "Tender Data"

#     # Write headers
#     for col, header in enumerate(headers, start=1):
#         ws.cell(row=1, column=col, value=header)

#     # Write data
#     for row, record in enumerate(data, start=2):
#         for col, value in enumerate(record, start=1):
#             cell = ws.cell(row=row, column=col, value=value)
#             if col == 3:  # Link column
#                 cell.hyperlink = Hyperlink(ref=f'#{value}', location=value, target=value)
#                 cell.value = record[1]  # Use the Name as the display text
#                 cell.style = "Hyperlink"

#     # Adjust column widths
#     for col in ws.columns:
#         max_length = 0
#         column = col[0].column_letter
#         for cell in col:
#             try:
#                 if len(str(cell.value)) > max_length:
#                     max_length = len(cell.value)
#             except:
#                 pass
#         adjusted_width = (max_length + 2)
#         ws.column_dimensions[column].width = adjusted_width

#     wb.save(filename)

def readFilters():
    global filters
    try:
        with open('filters.csv', mode='r', newline=None) as file:
            reader = csv.reader(file, delimiter='\n', quoting=csv.QUOTE_NONE)
            filters = [row[0].strip() for row in reader]
    except FileNotFoundError:
        print(f'No filters.csv file found')
    except Exception as e:
        print(f'Error when reading filters: {e}')

def createDatabase():
    try: 
        df = pd.DataFrame(columns = headers)
        df.to_csv(database, index=False) # Write the headers to CSV file
    except Exception as e:
        print(f'Error occurred in creating database file: {e}')

def getIDs():
    global IDarray
    try: 
        df = pd.read_csv(database)

        # Check if the DataFrame is empty
        if df.empty or not ('ID' in df.columns):
            createDatabase()
            return False
        else: 
            # Extract the ID column
            IDarray = df['ID'].astype(str).tolist()
            return True
    except FileNotFoundError:
        createDatabase()
        return False

# getIDs function for pandas
def getIDs_pd():
    global IDarray
    try: 
        IDarray = pd.read_excel(database, usecols="A", header=0, index_col=None, dtype=str).values.flatten()
    except FileNotFoundError:
        print(f"database.xlsx for {current_year} does not exist")
    except Exception as e:
        print(f"Error when trying to access database.xlsx for {current_year}: {e}")

def soupify(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def get_pdf_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag_text = soup.find('body').find('script').getText()
    return "https://www.ha.org.hk" + re.search(r"/.*?\.pdf", script_tag_text).group()
 
def make_valid_pdf_name(s):
    return s.translate(str.maketrans('', '', r'!@#$()-/\\')).strip()

def sanitize_text(text): # For hyperlink names in the csv file
    # Remove or replace problematic characters
    return text.replace('"', '""').replace('\n', ' ').replace('\r', '')

def download_pdf(name, id, url, closing_date, hospital):
    pdf = requests.get(url)
    safe_id = make_valid_pdf_name(id) # Remove chars not allowed in PDF file name
    path = os.path.join(download_folder, safe_id + ".pdf")
    print(f"Downloading: {url}")
    with open(path, 'wb') as f:
        f.write(pdf.content)
    
    matched_filters = []

    # Create shortcuts
    for filter in filters:
        eldar = Query(filter, match_word=False)
        if eldar(name):
            matched_filters.append(filter)
            shortcut_folder_name = filter.replace(" ", "_").replace('"','').translate(str.maketrans('', '', "!@#$()-/\\"))
            shortcut_folder_path = os.path.join(shortcuts_folder, shortcut_folder_name)
            os.makedirs(shortcut_folder_path, exist_ok=True)
            shortcut_path = os.path.join(shortcut_folder_path, safe_id + ".lnk")
            shortcut_target = path
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = shortcut_target
            shortcut.save()

    internal_link = f'file://{path}'
    mappings.append([id, name, f'=HYPERLINK("{internal_link}", "{sanitize_text(name)}")', today.strftime("%d-%m-%Y").strip('"'), closing_date, hospital, ",".join(str(bit) for bit in matched_filters)])

#### BEGIN MAIN ####

start_soup = soupify(start_url)

tender_notice1_url = "https://www.ha.org.hk/visitor/" + start_soup.find('a', string="TENDER NOTICES")['href']
tender_notice1_soup = soupify(tender_notice1_url)
tender_notice1_script_tag_text = tender_notice1_soup.find('body').find('script').getText()
tender_notice1_htm_url = "https://www.ha.org.hk" + re.search(r"/.*?\.htm", tender_notice1_script_tag_text).group()

tender_notice2_soup = soupify(tender_notice1_htm_url)
table = tender_notice2_soup.find('table')

getIDs_pd() #getIDs()

for row in table.find_all('tr')[1:]: # Skip header row
    cols = row.find_all('td')
    if len(cols) < 4:
        continue

    tender_doc_id = cols[0].find('p').getText()

    if tender_doc_id in IDarray:
        continue

    tender_doc_link_tag = cols[1].find('a')
    closing_date = cols[2].find('p').getText()
    hospital = cols[3].find('p').getText()
    tender_doc_url = tender_doc_link_tag['href']
    tender_doc_name = tender_doc_link_tag.getText()
    tender_doc_soup = soupify(tender_doc_url)
    print(f"ID: {tender_doc_id}, URL: {tender_doc_name}, Hospital: {hospital}, Closing Date: {closing_date}")
    tender_doc2_url = tender_doc_soup.find('a')['href']
    download_pdf(tender_doc_name, tender_doc_id, get_pdf_url(tender_doc2_url), closing_date, hospital)

# with open(database, mode='a', newline='', encoding='utf-8-sig') as file:
#     writer = csv.writer(file)
#     #  writer.writerow(headers)  # Header
#     writer.writerows(mappings)



