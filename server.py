from flask import Flask, render_template, request, jsonify, make_response
from info import classify2, classify3
from math import e
from redis import Redis
from config import STATS_KEY, HOST, RHOST, RPASS, RPORT, LOG_FILE
from cors import crossdomain
from datetime import datetime
import json
import requests
from hammock import Hammock as GendreAPI
from gender_dict import gender as gender_dict
import goslate
from info import lang_detect_level1
from info import lang_detect_level2
from info import lang_detect_level3
import logging
import re
from textblob import TextBlob
from info import LangDetect
from textblob.sentiments import NaiveBayesAnalyzer


app = Flask(__name__)
app.debug = False
app.config['MAX_CONTENT_LENGTH'] = (1 << 20) # 1 MB max request size
#conn = Redis(RHOST, RPORT, password=RPASS)
sentiment_dict = {'neg': 'Negative', 'pos': 'Positive', 'neutral': 'Neutral'}
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

def percentage_confidence(conf):
	return 100.0 * e ** conf / (1 + e**conf)

def today():
	return datetime.now().strftime('%Y-%m-%d')

def get_sentiment_route(text, web=False):
	if web == 'facebook':
		return  get_sentiment_facebook(text)
	else:
		return get_sentiment_textblob(text)

# def get_sentiment_browse(text):
# 	logging.debug(' in browser ')
# 	flag, confidence = classify3(text)
# 	if confidence > 0.5:
# 		sentiment = "Positive" if flag else "Negative"
# 	else:
# 		sentiment = "Neutral"
# 	conf = "%.4f" % percentage_confidence(confidence)
# 	return (sentiment, conf)

def get_sentiment_facebook(text):
	logging.debug(' in facebook ')
	try:
		response = requests.post('http://text-processing.com/api/sentiment/', data={'text': text})
	except requests.exceptions.ConnectionError as e:
		response = False
	if response and response.status_code == 200:
		res_dict = json.loads(response.content)
		try:
			conf = "%.4f" % percentage_confidence(res_dict['probability'][res_dict['label']])
			sentiment = sentiment_dict[res_dict['label']]
			return (sentiment, conf)
		except Exception, e:
			print e
	else:
		return get_sentiment_textblob(text)


def get_sentiment_textblob(text):
	try:
		testimonial = TextBlob(text)
		polarity = testimonial.sentiment.polarity
		print polarity
		if polarity > 0:
			return 'positive',  "%.4f" % percentage_confidence(polarity)
		elif polarity < 0:
			return 'negative',  "%.4f" % percentage_confidence(polarity)
		elif polarity == 0:
			return 'nuteral', "%.4f" % percentage_confidence(polarity)
	except Exception, e:
		logging.debug(' Exception Textblob ' + str(e))
		return get_sentiment_info(text)

def get_sentiment_info(text):
	flag, confidence = classify2(text)
	if confidence > 0.5:
		sentiment = "Positive" if flag else "Negative"
	else:
		sentiment = "Neutral"
	conf = "%.4f" % percentage_confidence(confidence)
	return (sentiment, conf)

@app.route('/')
def home():
	#conn.incr(STATS_KEY + "_hits")
	return render_template("index.html")

@app.route('/api/text/', methods=["POST"])
@crossdomain(origin='*')
def read_api():
	text = request.form.get("txt", '')
	# text = text.replace('Telenor ', ' ')
	web = request.form.get('web', False)
	translated = re.sub(r"http\S+", "", text)
	try:
		translated = re.sub("\$(\w+) ", "", text)
	except Exception, e:
		print str(e)
	translated = translated.replace('#', ' ')
	print translated
	lang = LangDetect()
	lang_d = lang.detect(translated)
	if lang.detect(translated) != 'en':
		translated = lang.translate(translated, lang_d)
	print translated
	#blob = TextBlob(translated)
	# if blob.detect_language() != 'en':
	# 	translated = blob.translate(to='en')
	# print translated
	sentiment, confidence = get_sentiment_route(translated, web=web)
	result = {"sentiment": sentiment, "confidence": confidence}
	#conn.incr(STATS_KEY + "_api_calls")
	#conn.incr(STATS_KEY + today())
	return jsonify(result=result)

@app.route('/web/text/', methods=["POST"])
@crossdomain(origin='*')
def evaldata():
	text = request.form.get("txt")
	result, confidence = get_sentiment_info(text)
	#conn.incr(STATS_KEY + "_web_calls")
	#conn.incr(STATS_KEY + today())
	return jsonify(result=result, confidence=confidence, sentence=text)

@app.route('/api/batch/', methods=["POST"])
@crossdomain(origin='*')
def batch_handler():
	json_data = request.get_json(force=True, silent=True)
	if not json_data:
		return jsonify(error="Bad JSON request")
	result = []
	for req in json_data:
		sent, conf = get_sentiment_info(req)
		result.append({"result": sent, "confidence": conf})

	#conn.incrby(STATS_KEY + "_api_calls", len(json_data))
	#conn.incrby(STATS_KEY + today(), len(json_data))
	resp = make_response(json.dumps(result))
	resp.mimetype = 'application/json'

	return resp

@app.route('/docs/api/')
def api():
	return render_template('api.html', host=HOST)

@app.route('/about/')
def about():
	return render_template('about.html')


@app.route('/api/gender/', methods=["POST"])
@crossdomain(origin='*')
def gender_detection():
	"""
	This method check in the dictionary /gender_dict.py if the name find in it returns it gender and if
	this dict has no key for that name it checks for the free service to identify the gender.
	API source code is at
	:return:
	"""
	result = {}
	first_name = request.form.get("first_name", '')

	if not first_name:
		result.update({'status': False, 'msg': 'Please provide first_name it is mandatory!'})
		return jsonify(result=result)
	else:
		names = first_name.split(' ')
		print names, "names"
		for name in names: # Loop will continue until gender detected or it is found in our dict.
			try:
				# Check if the gender is in our dictionary
				if name.lower() not in gender_dict:
					gendre = GendreAPI("http://api.namsor.com/onomastics/api/json/gendre")
					resp = gendre(name, 'a').GET()
					gender = resp.json().get('gender', '')
				else:
					gender = gender_dict[name.lower()]
					if gender.lower() != 'male' and gender.lower() != 'female':
						result.update({'status': True, 'gender': 'Unknown'})
						break
				if gender.lower() == 'male' or gender.lower() == 'female':
					result.update({'status': True, 'gender': gender})
					break
			except Exception, e:
				print str(e)
				result.update({'status': False, 'gender': 'Unknown'})
		return jsonify(result=result)


@app.route('/api/lang/', methods=["POST"])
@crossdomain(origin='*')
def lang_detection():
	result = {'language_id': 0, 'language': 'Not Detected'}
	lang = request.form.get('txt', '')
	lang = re.sub(r"http\S+", "", lang)  # Links Removed
	# removing hash tags
	# hash_at_tags = re.findall(r'(?i)\#\w+', lang)
	# hash_at_tags += re.findall(r'(?i)\@\w+', lang)
	# print hash_at_tags
	text_list = lang.replace('#', ' ').split()
	lang = ' '.join([i for i in text_list if len(i) < 20 ])
	if len(lang):
		gs = goslate.Goslate()  # will use this object in all services.
		# TextBlob free service powered by google
		try:
			result = lang_detect_level1(lang, gs)
			return jsonify(result=result)
		except Exception, e:
			print str(e)
			logging.debug('Error in level 1' + str(e))
		# Paid service, Free 5000 records per day
		try:

			result = lang_detect_level2(lang, gs)
			return jsonify(result=result)
		except Exception, e:
			logging.debug('Error in level 2' + str(e))
		result = lang_detect_level3(lang, gs)
	return jsonify(result=result)

#
# @app.route('/api/comparison/', methods=["GET"])
# @crossdomain(origin='*')
# def comparison():
# 	import pypyodbc
# 	connection = pypyodbc.connect('Driver={SQL Server};'
# 								  'Server=192.168.7.208;'
# 								  'Database=Insight360_Outfitters;'
# 								  'uid=nestleclearview;pwd=n3$tle')
#
# 	cursor = connection.cursor()
# 	SQLCommand = ("SELECT [id], [message] FROM [Insight360_Outfitters].[dbo].[Staging_Facebook_Posts]")
# 	Values = [2]
# 	try:
# 		cursor.execute(SQLCommand)
# 		results = cursor.fetchall()
# 	except Exception, e:
# 		print str(e)
#
# 	print len(results)
# 	response = []
# 	for result in results:
# 		sentiment = []
# 		s, c = get_sentiment_facebook(result[1])
# 		sentiment.append(s)
# 		s1, c = get_sentiment_textblob(result[1])
# 		sentiment.append(s1)
# 		resp = requests.post('http://192.168.7.208:86/api/text/', data={
# 			'txt': result[1], 'web': 'facebook'})
# 		data = 0
# 		if resp.status_code == 200:
# 			data = json.loads(resp.content)
# 			data = data['result']['sentiment']
# 		sentiment.append(data)
# 		response.append(sentiment)
#
# 	connection.close()
#
# 	return jsonify(result=response)