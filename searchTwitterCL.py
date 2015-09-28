# -*- coding: utf-8 -*-

# NLDS Lab
# Nicolas Hahn
# Search Twitter using their search API
# Take one or multiple queries
# Get recent tweets that match the query
# Put each into its own separate file in the queries folder

# go through steps to register Twitter app
# create a file called 'settings.py' and put the following 4 lines in (with your info):
# access_token          = '...'
# access_token_secret   = '...'
# consumer_key          = '...'
# consumer_secret       = '...'

from TwitterSearch import *
from settings import consumer_key, consumer_secret, access_token, access_token_secret
from getpass import getpass
import sys
import pickle
from json import dumps as jDumps
import datetime

alphaChars = 'abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUWXYZ#@'

currtime = str(datetime.datetime.now())
currtime = currtime.replace(' ','-').replace(':','-').split('.')[0]

queriesFolder = '/home/nick/TwitterSearchToDatabase/queries'

def searchQuery(ts, query):
    print('Searching for: '+query)
    tso = TwitterSearchOrder()
    keywords = query.split(' ')
    tso.set_keywords(keywords)
    tso.set_language('en')
    tso.set_include_entities(True)

    out_file_name = 'query-'+''.join([q for q in query if q in alphaChars])
    out_file_name += '-'+currtime
    output = open(queriesFolder+"/"+out_file_name, 'w', encoding='utf-8')

    i = 0
    for tweet in ts.search_tweets_iterable(tso):
        i += 1
        # changes single to double quotes, so json.load() works later
        jsonTweet = jDumps(tweet)
        output.write(jsonTweet+'\n')
    output.close()
    print('query "'+query+'" got '+str(i)+' tweets')

def main():

    if len(sys.argv) < 2:
        print("Usage: python3 searchTwitterCL.py '#query1' 'query2' 'query3' etc.")
        exit()  

    ts = TwitterSearch(
        consumer_key = consumer_key,
        consumer_secret = consumer_secret,
        access_token = access_token,
        access_token_secret = access_token_secret
        )
    
    queries = sys.argv[1:]
    # for i in range(1,len(sys.argv)):
    #     queries.append(sys.argv[i])
    # n = input("Enter number of search queries: ")
    # for i in range(int(n)):
    #   queries.append(input("Enter query: "))
    # print("Enter queries followed by return. When done submit empty query.")
    # while True:
    #     query = input("Enter query: ")
    #     if query != "":
    #         queries.append(query)
    #     else: 
    #         break
        

    for query in queries:
        try:
            searchQuery(ts, query)
        except TwitterSearchException as e:
            print(e)

if __name__ == "__main__":
    main()
