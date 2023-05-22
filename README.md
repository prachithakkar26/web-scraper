# Formula 1 Race Data Scraper

This Python script scrapes race data from the Formula 1 website for multiple years and saves it to an Excel file.

## Prerequisites

To run this code, you need to have the following libraries installed:

    - BeautifulSoup (`bs4`)
    - Requests (`requests`)
    - Pandas (`pandas`)
    - Openpyxl (`openpyxl`)

You can install these libraries using pip:

    pip install beautifulsoup4 requests pandas openpyxl


## Usage

1. Import the required libraries:

```python
from bs4 import BeautifulSoup
import requests
import pandas as pd
from openpyxl import Workbook
```

2. Define the Formula 1 website URLs for the desired years:

```python
F1_urls = [
    'https://www.formula1.com/en/results.html/2022/drivers.html',
    'https://www.formula1.com/en/results.html/2021/drivers.html'
]
```

3. Scrape race data for each year and driver:

```python
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

```

4. Concatenate all race data into a single DataFrame:

```python
all_races_df = pd.concat(all_races)
```

5. Drop the unnamed columns:

```python
all_races_df = all_races_df.drop(columns=all_races_df.columns[all_races_df.columns.str.contains('unnamed', case=False)])
```

6. Save the data to an Excel file:

```python
all_races_df.to_excel("races.xlsx", index=False)
```