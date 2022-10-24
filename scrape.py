'''
Scraping data from EDGAR Files
Reference: Using AAPL's recent 10-K
'''

# Libraries to scrape and parse data
import requests
from bs4 import BeautifulSoup
import json
from openpyxl import load_workbook

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

all_info = {}

'''
Make dealing with numbers a bit easier
'''
def strip_vals(text_val):
    curr_value = text_val.replace(",", "")
    curr_value = curr_value.replace("(", "")
    curr_value = curr_value.replace(")", "")
    curr_value = curr_value.replace("%", "")
    curr_value = curr_value.replace("—", "")
    return int(curr_value)

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
def find_category(form_data, categories, official_name, is_balance_sheet):
    # Finding the data
    for table in form_data:
        for row in table:
            selected_string = (row[0].lower())
            for category in categories:
                if (isinstance(category, str)):
                    if (selected_string == category):
                        print(selected_string)
                        print(category)
                        print(row)
                        print("")
                        if (not is_balance_sheet and len(row) == 4):
                            if (official_name not in all_info):
                                all_info[official_name] = row[1:]
                        if (is_balance_sheet and len(row) == 3):
                            if (official_name not in all_info):
                                all_info[official_name] = row[1:]
                else:
                    # Create initial array within all_info
                    if official_name not in all_info:
                        all_info[official_name] = [0] * 2
                        if (is_balance_sheet):
                            all_info[official_name].append(0)
                    
                    seen_rows = []
                    for line in category:
                        if (selected_string == line and row not in seen_rows):
                            seen_rows.append(row)
                            for i in range(1, len(row)):
                                all_info[official_name][i-1] += (strip_vals(row[i]))
    
    # Error at the end
    if (official_name not in all_info):
        if (not is_balance_sheet):
            all_info[official_name] = [0, 0, 0]
        else:
            all_info[official_name] = [0, 0]
    

'''
Editing the spreadsheet of all data
'''
def edit_spreadsheet(file_name, mapping, save_file):
    # Open the Spreadsheet and find the corresponding values
    workbook = load_workbook(file_name)

    # Iterate through the JSON and see what we need
    m = open(mapping)
    data = json.load(m)

    # Iterate and update corresponding categories
    for category in data["nbs_metrics"]:
        for i in range(len(data["nbs_metrics"][category])):
            curr_value = all_info[category][i]
            if (isinstance(curr_value, str)):
                curr_value = strip_vals(curr_value)
            workbook["FSM Model Complete Output"][data["nbs_metrics"][category][i]] = int(curr_value)


    for category in data["bs_metrics"]:
        for i in range(len(data["bs_metrics"][category])):
            curr_value = all_info[category][i]
            if (isinstance(curr_value, str)):
                curr_value = strip_vals(curr_value)
            workbook["FSM Model Complete Output"][data["bs_metrics"][category][i]] = int(curr_value)
    
    for category in data["sep_metrics"]:
        for i in range(len(data["sep_metrics"][category])):
            workbook["FSM Model Complete Output"][data["sep_metrics"][category][i]] = all_info[category][i]

    # Save workbook    
    workbook.save('saved/' + save_file + '.xlsx')


'''
Main function to simply get all data
'''
def create_filled_spreadsheet(url, file_name):
    # Grab form data
    soup = make_request(url)
    form_data = get_table_data(soup)
    
    # Read in JSON file
    f = open('reference/formatting.json')
    data = json.load(f)

    # Read in the non balance sheet metrics
    for category in data["nbs_metrics"]:
        find_category(form_data, data["nbs_metrics"][category], category, False)

    # Read in balance sheet metrics
    for category in data["bs_metrics"]:
        find_category(form_data, data["bs_metrics"][category], category, True)

    for category in data["sep_metrics"]:
        all_info[category] = [0, 0, 0]
    
    spreadsheet_file = "spreadsheets/Banker.io Automated DCF FSMs Template V3.xlsx"
    edit_spreadsheet(spreadsheet_file, "reference/mapping.json", file_name)