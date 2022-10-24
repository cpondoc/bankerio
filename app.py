from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory
import json
from requests import get
import urllib.request, json 
from scrape import create_filled_spreadsheet

app = Flask(__name__)

# Get data on all companies
f = open('reference/sec.json')
company_data = json.load(f)

'''
Gets the URL for a company
'''
def find_report_url(company, form_name):
    co_dat = open('json/' + company + '.json')
    co_dat_json = json.load(co_dat)
    a_nums = (co_dat_json['filings']['recent']['accessionNumber'])
    report_dates = (co_dat_json['filings']['recent']['reportDate'])
    forms = (co_dat_json['filings']['recent']['form'])
    for i in range(len(a_nums)):
        if (forms[i] == form_name):
            cik = co_dat_json["cik"]
            access_number = a_nums[i].replace("-", "")
            report_date = report_dates[i].replace("-", "")
            url = "https://www.sec.gov/Archives/edgar/data/" + cik + "/" + access_number + "/" + company + "-" + report_date + ".htm"
            if (company == "msft"):
                url = "https://www.sec.gov/Archives/edgar/data/" + cik + "/" + access_number + "/" + company + "-10k_" + report_date + ".htm"
            if (company == "meta"):
                url = "https://www.sec.gov/Archives/edgar/data/" + cik + "/" + access_number + "/" + "fb-" + report_date + ".htm"
            return url

@app.route("/", methods=('GET', 'POST'))
def index():
    if request.method == "GET":
        companies = []
        for key in company_data:
            companies.append(key)
        return render_template("index.html", companies=companies)
    if request.method == "POST":
        company = request.form['company']
        form_name = request.form['form']
        scrape_url = find_report_url(company.lower(), form_name)
        print(scrape_url)
        create_filled_spreadsheet(scrape_url, company.lower())
        return redirect(url_for('download', ticker=company.lower()))

@app.route('/reports/<path:filename>')
def send_report(filename):
    return send_from_directory('saved/', filename)

@app.route('/download/<path:ticker>')
def download(ticker):
    return render_template('download.html', link="/reports/" + ticker + ".xlsx")