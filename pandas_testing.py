import pandas as pd
import os
from datetime import date

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

# getIDs function
def getIDs():
    global IDarray
    IDarray = pd.read_excel(database, usecols="A", header=0, index_col=None, dtype=str).values.flatten()
getIDs()

print(IDarray)
