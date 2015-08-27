# -*- coding: utf-8 -*-

# NLDS Lab
# Nicolas Hahn
# Search Twitter using their search API
# Download tweets to given output file

# create a file called 'settings' and put the following 4 lines in (with your info):
# access_token		 	= '...'
# access_token_secret 	= '...'
# consumer_key			= '...'
# consumer_secret		= '...'

from TwitterSearch import *
from settings import consumer_key, consumer_secret, access_token, access_token_secret
from getpass import getpass
import sys
import pickle
from json import dumps as jDumps

alphaChars = 'abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUWXYZ#@'

def searchQuery(ts, query):
	print('Searching for: '+query)
	tso = TwitterSearchOrder()
	keywords = query.split(' ')
	tso.set_keywords(keywords)
	tso.set_language('en')
	tso.set_include_entities(True)

	out_file_name = 'query-'+''.join([q for q in query if q in alphaChars])
	output = open(out_file_name, 'w', encoding='utf-8')

	i = 0
	for tweet in ts.search_tweets_iterable(tso):
		i += 1
		# changes single to double quotes, so json.load() works later
		jsonTweet = jDumps(tweet)
		output.write(jsonTweet+'\n')
	output.close()
	print('query "'+query+'" got '+str(i)+' tweets')

def main():

	ts = TwitterSearch(
		consumer_key = consumer_key,
		consumer_secret = consumer_secret,
		access_token = access_token,
		access_token_secret = access_token_secret
		)

	queries = []
	n = input("Enter number of search queries: ")
	for i in range(int(n)):
		queries.append(input("Enter query: "))

	for query in queries:
		try:
			searchQuery(ts, query)
		except TwitterSearchException as e:
			print(e)

if __name__ == "__main__":
	main()
