'''
Scraping data from EDGAR Files
Reference: Using AAPL's recent 10-K
'''

# Libraries to scrape and parse data
import requests
from bs4 import BeautifulSoup
import json

# Change URL here, add in data
# To-Do: programmatically get all the necessary data information using open .json, and then identify each.
'''
Process is as follows:
-Use data.sec.gov API: https://www.sec.gov/edgar/sec-api-documentation
-Then find corresponding form you need
-Then get corresponding URL you need
-Then get CIK
-Then use format below of: https://www.sec.gov/Archives/edgar/data/[CIK]/[ACCESSION-NUMBER-NO-DASHES]/[URL]
'''
url = "https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925.htm"


all_info = {
    'total net sales': []
}

'''
Make a request to EDGAR database
'''
def make_request(url):
    # Header format from EDGAR standards
    headers = {'User-Agent': 'Sample Company Name AdminContact@<sample company domain>.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

'''
Get data from each table, by iterating row by row
-Wondering if we'll have to iterate through to find "consolidated" tags, and then also label the tables, as well.
'''
def get_table_data(soup):
    # Identify table data and extract all
    form_data = []
    tables = soup.findAll("table")
    for table in tables:
        # Initialize new set od ata
        table_data = []

        # Grab all pertinent rows, and extract each
        rows = table.find_all('tr')
        for row in rows:
            # Go through each data cell, strip text
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]

            # Add a new row if not empty
            new_row = [ele for ele in cols if (ele and ele != "$")]
            if (len(new_row) != 0):
                table_data.append(new_row)
        
        # Append to existing form data
        if (len(table_data) != 0):
            form_data.append(table_data)
    
    return form_data

'''
Using a list of potential names for a category, grab the relevant data.

BIG ASSUMPTION: no row header will be utilized twice.
'''
def find_category(form_data, categories, is_balance_sheet):
    for table in form_data:
        for row in table:
            selected_string = (row[0].lower())
            for category in categories:
                if (selected_string == category):
                    if (not is_balance_sheet and len(row) == 4):
                        all_info[category] = row[1:]

'''
Main function to simply get all data
'''
if __name__ == "__main__":
    # Grab form data
    soup = make_request(url)
    form_data = get_table_data(soup)
    
    # Read in JSON file
    f = open('formatting.json')
    data = json.load(f)

    # Read in the non balance sheet metrics
    for category in data["nbs_metrics"]:
        find_category(form_data, data["nbs_metrics"][category], False)
    
    print(all_info)
