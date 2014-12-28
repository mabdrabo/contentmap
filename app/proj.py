# coding: utf-8
import os, sys
reload(sys)
sys.setdefaultencoding("utf-8")

from flask import Flask, render_template, request, url_for
from datetime import datetime
import pickle
import requests
# from lxml import html
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


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

import time
def wait_for(condition_function):
	start_time = time.time()
	while time.time() < start_time + 3:
		if condition_function():
			return True
		else:
			time.sleep(0.1)
	raise Exception(
		'Timeout waiting for {}'.format(condition_function.__name__)
	)


class wait_for_page_load(object):
	def __init__(self, driver):
		self.browser = driver
	def __enter__(self):
		self.old_page = self.browser.find_element_by_tag_name('html')
	def page_has_loaded(self):
		new_page = self.browser.find_element_by_tag_name('html')
		return new_page.id != self.old_page.id
	def __exit__(self, *_):
		wait_for(self.page_has_loaded)


@app.route('/')
def home():
	# countries = get_countries()
	# categories = get_categories()
	
	driver = webdriver.Firefox()
	driver.implicitly_wait(10)
	with wait_for_page_load(driver):
		driver.get('http://www.google.com/trends/topcharts#vm=cat&geo=EG&date=2014&cid')
		results = {}
		res = {}
		containers = driver.find_elements_by_class_name('topcharts-smallchart')
		for container in containers:
			title = container.find_element_by_class_name('topcharts-smallchart-title-link')
			container.find_element_by_class_name('topcharts-smallchart-title-list-container').click()
			time.sleep(2)
			names = driver.find_elements_by_class_name('topcharts-detailedchart-entity-title-in-list')
			results[title.text] = [unicode(name.text) for name in names]

			ActionChains(driver).send_keys(Keys.ESCAPE).perform()
		for k, v in results.iteritems():
			res[k] = []
			for name in v:
				driver.get('http://www.google.com/search?q=%s'%('+'.join(name.split())))
				elems = driver.find_elements_by_class_name('g')
				for elem in elems:
					print elem.text
				time.sleep(2)

		print results
	driver.quit()
	return render_template('home.html', results=results)


@app.route('/topsy')
def topsy():
	q1 = request.args.get('q1', None)
	q2 = request.args.get('q2', None)
	q3 = request.args.get('q3', None)
	print q1
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
