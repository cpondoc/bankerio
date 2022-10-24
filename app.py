from flask import Flask, render_template
import json
from requests import get
import urllib.request, json 

app = Flask(__name__)

# Get data on all companies
f = open('sec.json')
company_data = json.load(f)

@app.route("/")
def hello_world():
    companies = []
    for key in company_data:
        companies.append(key)
    return render_template("index.html", companies=companies)

for company in company_data:
    url = "https://data.sec.gov/submissions/CIK" + company_data[company] + ".json"
    print(url)
