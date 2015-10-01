# -*- coding: utf-8 -*-

# NLDS Lab
# Nicolas Hahn
# get parent tweet_ids from database
# search for them, get their JSON objects
# add to queries folder
import sqlalchemy as s
import oursql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import func
from TwitterSearch import *
from settings import consumer_key, consumer_secret, access_token, access_token_secret
from getpass import getpass
import sys
import os
from json import dumps as jDumps
import datetime
import time

# allowed chars for filenames
alphaChars = 'abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUWXYZ#@'

# timestamp formatted for filename
currtime = str(datetime.datetime.now())
currtime = currtime.replace(' ','-').replace(':','-').split('.')[0]

queriesFolder = '/home/nick/TwitterSearchToDatabase/queries'
oldParentIdFile = '/home/nick/TwitterSearchToDatabase/get_parents/parent_ids'
outFile = queriesFolder+'/parent-tweets-'+currtime

#########
# MySQL #
#########

# open connection to database
# then return engine object
def connect(username, password, database):
    db_uri = 'mysql+oursql://{}:{}@{}'.format(username, password, database)
    engine = s.create_engine(db_uri, encoding='utf-8')
    engine.connect()
    return engine

# create a session from the engine
def createSession(eng):
    Session = s.orm.sessionmaker()
    Session.configure(bind=eng)
    session = Session()
    return session

def generateTableClasses(eng):
    ABase = automap_base()
    ABase.prepare(eng,reflect=True)
    global Tweet
    Tweet = ABase.classes.tweets

# get all the non-null parent tweet ids, native ids as a list of tuples
def getParentTweetIds(session):
    query = session.query(Tweet).\
                filter(Tweet.in_reply_to_tweet_id > 0)
    parent_ids = []
    for t in query.all():
        parent_ids.append((t.in_reply_to_tweet_id,t.in_reply_to_native_tweet_id))
    return parent_ids

##################
# Old Parent Ids #
##################

# get the old parent ids from the file
def getOldParentIds(oldFile):
    old_parent_ids = []
    with open(oldFile,'r') as f:
        for line in f:
            iac_id, native_id = line.split()
            old_parent_ids.append((int(iac_id),native_id))
    return old_parent_ids

# write the new parent ids to the file
# def writeNewParentIds(new_ids, oldFile):
#     with open(oldFile,'a') as f:
#         for iac_id, native_id in new_ids:
#             f.write(str(iac_id)+" "+native_id+'\n')

# write single parent id to old parent file
def recordParentId(iac_id, native_id, parentFile):
    with open(parentFile,'a') as f:
        f.write(str(iac_id)+' '+native_id+'\n')
    

###########################
# searchTwitter functions #
###########################

# search for each parent's native twitter id, should get 1 result per query
# record the json data in a file in queries folder, and save the iac and native ids
def searchQuery(ts, query, outFile):
    print('Searching for: '+query)
    tso = TwitterSearchOrder()
    keywords = query.split(' ')
    tso.set_keywords(keywords)
    tso.set_language('en')
    tso.set_include_entities(True)
    with open(outFile,'a') as output:
        for tweet in ts.search_tweets_iterable(tso):
            # changes single to double quotes, so json.load() works later
            jsonTweet = jDumps(tweet)
            output.write(jsonTweet+'\n')

########
# Main #
########

def main(user=sys.argv[1],pword=sys.argv[2],db=sys.argv[3]):

    ts = TwitterSearch(
        consumer_key = consumer_key,
        consumer_secret = consumer_secret,
        access_token = access_token,
        access_token_secret = access_token_secret
        )
    
    # sqlalchemy magic
    print('Connecting to database',db,'as user',user)
    eng = connect(user, pword, db)
    metadata = s.MetaData(bind=eng)
    session = createSession(eng)
    generateTableClasses(eng)
    # get list of old parent ids that are already in db
    print("Getting parent tweet ids from database")
    parent_ids = getParentTweetIds(session)
    if os.path.exists(oldParentIdFile):
        old_parent_ids = getOldParentIds(oldParentIdFile)
    else:
        old_parent_ids = []
        open(oldParentIdFile,'w')
    # get parent ids that aren't yet in database
    new_parent_ids = [i for i in parent_ids if i not in old_parent_ids]
    print(len(new_parent_ids),"new parent tweets found")
    # get the tweets with those ids and throw em in query folder
    i = 0
    for iac_id, native_id in new_parent_ids:
        i += 1
        if i <= 180:
            # search for the native parent id, record both the 
            # json in outFile, and the id in oldParentIdFile
            try:
                searchQuery(ts, native_id, outFile)
                recordParentId(iac_id, native_id, oldParentIdFile)
            except TwitterSearchException as e:
                print("TwitterSearchException (rate limited), waiting ~15 minutes")
                i = 0
                time.sleep(905)
        else:
            i = 0
            print("Waiting for ~15 minutes to avoid rate limit")
            # add 5 seconds just to be safe
            time.sleep(905)
    # append new tweet ids to log file of old ones
    # print("Writing tweets to file")
    # writeNewParentIds(new_parent_ids,oldParentIdFile)
    

if __name__ == "__main__":
    main()

