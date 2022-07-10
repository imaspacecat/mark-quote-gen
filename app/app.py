from flask import Flask, render_template, jsonify
import random, time, threading
import requests
import os
import json
from datetime import date, timedelta, datetime

# from get_user_tweets.py
# put bearer token here
bearer_token = "" # os.environ.get("BEARER_TOKEN")


class TwitterUser:
	def __init__(self, userName, bearer_token):
		self.__userName = userName
		self.__bearer_token = bearer_token
		self.__userId = self.getIdByUsername()
	
	# inlude {} in baseURL in place of userName
		
	def getIdByUsername(self):
		json_response = self.callAPI("https://api.twitter.com/2/users/by/username/{}".format(self.__userName), "")
		return json_response["data"]["id"]
		
	def getUserId(self):
		return self.__userId
		
	def getAllTweets(self):
		dateOfCreation = date(2022, 4, 2) # first mark tweet
		endDate = date.today()
		
		tweets = []
		initialCallJson = self.callAPI("https://api.twitter.com/2/users/{}/tweets".format(self.__userId), {"max_results": "5", "start_time": "2022-04-02T00:00:00.000Z", "end_time": str(endDate)+"T00:00:00.000Z"})
		initialPaginationToken = initialCallJson["meta"]["next_token"] 
		
		for i in range(len(initialCallJson["data"])):
					tweets.append(initialCallJson["data"][i])
					
		print(initialCallJson["meta"]["next_token"])
		
		try:
			while True:
				tokenCallJson = self.callAPI("https://api.twitter.com/2/users/{}/tweets".format(self.__userId), {"max_results": "100", "start_time": "2022-04-02T00:00:00.000Z", "end_time": str(endDate)+"T00:00:00.000Z", "pagination_token": initialPaginationToken})
				
				for i in range(len(tokenCallJson["data"])):
					tweets.append(tokenCallJson["data"][i])
				
				print(tokenCallJson)
				initialPaginationToken = tokenCallJson["meta"]["next_token"]
				
		except:
			print("skill issue")
			print(tweets)
			print("Succesfully yoinked " + str(len(tweets)) + " messages!")
			
		return tweets
		
	def bearer_oauth(self, r):
		r.headers["Authorization"] = "Bearer " + bearer_token
		return r


	def callAPI(self, url, params):
		response = requests.request("GET", url, auth=self.bearer_oauth, params=params)
		# print(response.status_code)
		if response.status_code != 200:
			raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))
		return response.json()


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

user = TwitterUser("Mark15798883", bearer_token)
tweets = user.getAllTweets()

def update_tweets():
	print("update_tweets thread started")
	global tweets
	global user
	while True:
		time.sleep(24 * 60 * 60)
		tweets = user.getAllTweets()
		print("tweets successfully updated")
		
update_tweets_thread = threading.Thread(target=update_tweets)
update_tweets_thread.start()

@app.route("/")
def main_page():
	initial_tweet = tweets[random.randint(0, len(tweets)-1)]
	return render_template("index.html", tweet=initial_tweet)
	
@app.route("/all")
def all_quotes():
	return render_template("all.html", tweets=tweets) # jsonify(tweets)



