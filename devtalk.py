# Daily Dev Talk Twitter Bot
# Ian Mobbs - ianmobbs.com

# Brute force solution
# Optimizations to be made:
# 	- Store old tweets every hour
# 	- Exclude tweets by same author
# 	- Create hashmap of tweets on retrieval with vector sum

# Imports
import tweepy						# Required to interface with Twitter
import re, math 					# Used to compare tweets
from os import environ as ENV 		# Used for environment variables
from collections import Counter			# Used vectorize tweets

# Tokens to access Twitter API
# from keys import consumer_key, consumer_secret, access_token, access_token_secret

# Token access from Heroku environment
consumer_key = ENV['consumer_key']
consumer_secret = ENV['consumer_secret']
access_token = ENV['access_token']
access_token_secret = ENV['access_token_secret']

# DailyDevTalk class
class DailyDevTalk(tweepy.StreamListener):
	# Connects to Twitter API
	def __init__(self):
		self.searches = [
			"#DevTalk",
			"#DevDiscuss",
		]
		print("Initialized")
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		self.api = tweepy.API(auth)

	# Starts searching for #DevTalk tweets
	def start(self):
		print("Streaming")
		stream = tweepy.Stream(auth = self.api.auth, listener=DailyDevTalk())
		stream.filter(track=self.searches, async="true")

	# Returns a counter of all words found in a tweet
	# TODO: Remove links and usernames from Tweet text
	def tweet_to_vector(self, text):
		WORD = re.compile(r'\w+')
		words = WORD.findall(text)
		ignored_words = ["the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with", "as", "do", "at", "devtalk", "devdiscuss", "rt"]
		counted_words = [word for word in words if word not in ignored_words]
		print(counted_words)
		print("Compared vector")
		return Counter(words)

	# Finds the cosine similarity of two tweets
	# TODO: Use hashmap of tweets with their vector sums
	# http://stackoverflow.com/questions/15173225/how-to-calculate-cosine-similarity-given-2-sentence-strings-python
	def compare_tweets(self, vec1, vec2):
		intersection = set(vec1.keys()) & set(vec2.keys())
		numerator = sum([vec1[x] * vec2[x] for x in intersection])

		sum1 = sum([vec1[x]**2 for x in vec1.keys()])
		sum2 = sum([vec2[x]**2 for x in vec2.keys()])
		denominator = math.sqrt(sum1) * math.sqrt(sum2)

		print("Compared tweets")

		if not denominator:
			return 0.0
		else:
			return float(numerator) / denominator
		
	# Finds previous 100 tweets
	# TODO: Cache tweets every day
	def get_previous_tweets(self): 
		print("Found previous tweets")
		return tweepy.Cursor(self.api.search, q=" OR ".join(self.searches)).items(100)

	# Finds and returns most similar tweets
	def get_most_similar_tweet(self, tweet):
		most_similar_tweet = None
		most_similar_tweet_similarity = 0
		tweet_vector = self.tweet_to_vector(tweet)
		for old_tweet in self.get_previous_tweets():
			second_tweet_vector = self.tweet_to_vector(old_tweet.text)
			new_similarity = self.compare_tweets(tweet_vector, second_tweet_vector)
			if new_similarity > most_similar_tweet_similarity:
				most_similar_tweet_similarity = new_similarity
				most_similar_tweet = old_tweet
		print("Found most similar tweets")
		if most_similar_tweet_similarity > 0.5:
			return most_similar_tweet, most_similar_tweet_similarity
		else:
			return None, None

	# Matches two tweets and connects the users
	def match_tweet(self, tweet):
		most_similar_tweet, most_similar_tweet_similarity = self.get_most_similar_tweet(tweet.text)
		if most_similar_tweet is not None:
			break_conditions = [
				most_similar_tweet.author == tweet.author,
				most_similar_tweet.author == 'DailyDevTalk',
				tweet.author == 'DailyDevTalk',	
			]
			if not any(break_conditions):
				self.api.update_status("@{3} It looks like @{0} is talking about this too! ({1:0.2f}% similarity) {2}".format(most_similar_tweet.author.screen_name, most_similar_tweet_similarity * 100, "http://twitter.com/%s/status/%s" % (most_similar_tweet.author.screen_name, most_similar_tweet.id), tweet.author.screen_name), in_reply_to_status_id=tweet.id)
		
		print("Matched tweet")

	# Follows, retweets, and favorites tweets using the #DevTalk hashtags
	def on_status(self, status):
		break_conditions = [
			status.text[0:2] == 'RT',
			status.author.screen_name == 'DailyDevTalk'
		]
		if not any(break_conditions):
			print("Received tweet")
			# Follow user
			self.api.create_friendship(status.author.screen_name)
			# Favorite tweet
			self.api.create_favorite(status.id)
			# Retweet tweet
			# TODO: Only retweet notable tweets
			#self.api.retweet(status.id)
			# Match up with user by tweet text
			self.match_tweet(status)


def main():
	# Runs the DailyDevTalk bot
	listener = DailyDevTalk()
	listener.start()

main()