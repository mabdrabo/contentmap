# coding: utf-8
import os, sys
reload(sys)
sys.setdefaultencoding("utf-8")

from flask import Flask, render_template, request, url_for
from datetime import datetime
import pickle
import requests
from lxml import html

_wd = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_url_path='/static')

COUNTRIES_PICKLE = 'countries.pickle'
CATEGORIES_PICKLE = 'categories.pickle'


def get_countries():
	if os.path.isfile(COUNTRIES_PICKLE):
		with open(COUNTRIES_PICKLE, 'rb') as handle:
			countries = pickle.load(handle)
	else:
		url = "http://www.alexa.com/topsites/countries"
		page = requests.get(url)
		tree = html.fromstring(page.text)
		lis = tree.xpath('//div[@class="categories top"]//li//a')
		countries = [{l.text: "http://www.alexa.com" + l.items()[0][1]} for l in lis]
		with open(COUNTRIES_PICKLE, 'wb') as handle:
			pickle.dump(countries, handle)
	return countries


def get_categories():
	if os.path.isfile(CATEGORIES_PICKLE):
		with open(CATEGORIES_PICKLE, 'rb') as handle:
			categories = pickle.load(handle)
	else:
		url = "http://www.alexa.com/topsites/category"
		page = requests.get(url)
		tree = html.fromstring(page.text)
		lis = tree.xpath('//div[@class="categories top"]//li//a')
		categories = [{l.text: "http://www.alexa.com" + l.items()[0][1]} for l in lis]
		with open(CATEGORIES_PICKLE, 'wb') as handle:
			pickle.dump(categories, handle)
	return categories


@app.route('/')
def home():
	countries = get_countries()
	categories = get_categories()
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
