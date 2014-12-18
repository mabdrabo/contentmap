# coding: utf-8
import os, sys
reload(sys)
sys.setdefaultencoding("utf-8")

from flask import Flask, render_template, request, url_for
from datetime import datetime

_wd = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_url_path='/static')

@app.route('/')
def home():
	import requests
	from lxml import html
	url = "http://www.alexa.com/topsites/countries"
	page = requests.get(url)
	tree = html.fromstring(page.text)
	lis = tree.xpath('//div[@class="categories top"]//li//a')
	countries = [{l.text: l.items()[0][1]} for l in lis]
	return render_template('home.html')


@app.route('/country')
def country():
	return render_template('country.html')


@app.route('/country_submit', methods=['POST'])
def country_submit():
	country = request.form['country']
	return render_template('report.html', country=country)

if __name__ == '__main__':
	app.run(debug=True)
