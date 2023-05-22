# Importing the libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
from openpyxl import Workbook

# Formula 1 website URLs
F1_urls = [
    'https://www.formula1.com/en/results.html/2022/drivers.html',
    'https://www.formula1.com/en/results.html/2021/drivers.html'
]

all_races = []

# Loop through years from 2022 to 2020 (in reverse order)
for year in range(2022, 2020, -1):
    for F1_url in F1_urls:
        try:
            response = requests.get(F1_url)
            response.raise_for_status()  # Raise an exception if the request was unsuccessful

            soup = BeautifulSoup(response.text, 'lxml')

            standings = soup.select('table.resultsarchive-table')[0]

            links = standings.find_all('a')  # Extract links for individual driver pages
            links = [l.get("href") for l in links]
            links = [l for l in links if '/drivers' in l]

            # Loop through each driver's page
            for driver_url in [f"https://www.formula1.com{l}" for l in links]:
                try:
                    response = requests.get(driver_url)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, 'lxml')

                    races = pd.read_html(str(soup.find('table')))[0] # Extract race data table

                    races["Season"] = year  # Adds column for the year and the driver name
                    races["Driver"] = driver_url.split("/")[-1].replace(".html", "").replace("-", " ")

                    all_races.append(races) # Append race data to the lis
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching data from {driver_url}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {F1_url}: {e}")

# Concatenate all race data into a single DataFrame
all_races_df = pd.concat(all_races)

# Drop the unnamed columns
all_races_df = all_races_df.drop(columns=all_races_df.columns[all_races_df.columns.str.contains('unnamed', case=False)])

# Save the data to an Excel file
all_races_df.to_excel("races.xlsx", index=False)
