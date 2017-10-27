import time
import requests
import re
import pytz

from datetime import datetime

from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import Markup

import urllib.request, json 

global feed

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def default():
	feed = get_news()
	return render_news(feed)

@app.route('/post/<string:post_id>')
def show_post(post_id):
	for t in feed[post_id] :
		# print(t['title'])
		text = "<p>"+t['text']+"</p>"
		tags = t['tags']


		for tag in tags :
			ins_text = re.compile(r'\b%s\b' % tag, re.IGNORECASE)
			text = ins_text.sub("<span class=\"tag\">"+tag+"</span>",text)

	order = list(reversed(sorted(feed.keys())))

	return render_template("home.html", articles=feed, order=order, id=post_id, text=text)

def format_datetime(value):
	iso_ts=str(value)
	t = datetime.strptime(iso_ts[2:18], '%Y-%m-%dT%H:%M')
	return t.strftime("%d %B %H:%M")	

app.jinja_env.filters['datetime'] = format_datetime

def get_news():
	feed = []

	json_url='http://www.iero.org/beatcrunch/'+time.strftime("%Y%m%d")+".json"
	with urllib.request.urlopen(json_url) as url:
		feed = json.loads(url.read().decode())

	return feed

def render_news(feed):
	order = list(reversed(sorted(feed.keys())))

	return render_template("home.html", articles=feed, order=order)

if __name__ == "__main__":

	feed = get_news()
	app.run(port=5000, debug=True)
