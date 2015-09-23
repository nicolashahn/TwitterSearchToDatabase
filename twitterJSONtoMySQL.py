# twitterJSONtoMySQL.py
# take JSON dump files from searchTwitter.py
# insert them into the IAC MySQL database

import json
import sqlalchemy as s
import oursql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.dialects import mysql
import sys
import re
import time

###################################
# Global variables
###################################

# because 1-5 appear to be taken in IAC
twitter_id = 7

# how many objects to push to server at a time
batch_size = 1000

# {native_id: db_id}
# so we don't have to query to check if author/whatever already in db
hashtag_dict = {}
author_dict = {}
# maps native tweet ids to db ids, includes tweets not in db
tweet_dict = {}
# for native tweet ids in the database
tweet_list = []

# temporary output file for checking things 
# (print statements choke on unicode)
tempOut = open('tempOut','w', encoding='utf-8')

###################################
# JSON data manipulation
###################################

# json text dump -> list of json-dicts
# also encodes the line number the object in the raw file
def jsonLineToDict(line):
	jObj = json.loads(line)
	jObj = removeNonUnicode(jObj)
	return jObj

# occasionally a char will not be in UTF8,
# this makes sure that all are
def removeNonUnicode(jObj):
	for field in jObj:
		if isinstance(jObj[field],str):
			# jObj[field] = jObj[field].decode('utf-8','ignore')
			jObj[field] = ''.join(i for i in jObj[field] if ord(i)<256)
			if jObj[field] == None:
				jObj[field] = ''
	return jObj

###################################
# MySQL general helper functions
###################################

# incrementer class for id fields
# each table class gets one
class Incrementer():
	def __init__(self,initial=0):
		self.i = initial

	def inc(self):
		self.i += 1
		return self.i

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

# 
def generateTableClasses(eng):
	ABase = automap_base()
	ABase.prepare(eng,reflect=True)
	global Tweet, Author, Text, Hashtag, HashtagRelation, UserMention 
	Tweet = ABase.classes.tweets 
	Author = ABase.classes.authors 
	Text = ABase.classes.texts 
	Hashtag = ABase.classes.hashtags 
	HashtagRelation = ABase.classes.hashtag_relations
	UserMention = ABase.classes.user_mentions

def generateIncrementers(tweet_dict, author_dict,hashtag_dict,hr_count,um_count):
	global tweet_inc, author_inc, hashtag_inc, user_mention_inc, hashtag_relation_inc
	t_count = 0
	if len(tweet_dict)>0:
		t_count = max([tweet_dict[i] for i in tweet_dict])
	tweet_inc = Incrementer(t_count)
	author_inc = Incrementer(len(author_dict))
	# text_inc = Incrementer(len(tweet_list))
	hashtag_inc = Incrementer(len(hashtag_dict))
	hashtag_relation_inc = Incrementer(hr_count)
	user_mention_inc = Incrementer(um_count)

#####################
# Database Querying #
#####################

def getAuthorsFromDatabase(session):
	aquery = session.query(Author).\
				filter(Author.dataset_id==twitter_id)
	author_dict = {}
	for a in aquery.all():
		author_dict[a.username] = a.author_id
	return author_dict

def getHashtagsFromDatabase(session):
	hquery = session.query(Hashtag).\
				filter(Hashtag.dataset_id==twitter_id)
	hashtag_dict = {}
	for h in hquery.all():
		hashtag_dict[h.hashtag_text] = h.hashtag_id
	return hashtag_dict

def getTweetsFromDatabase(session):
	tquery = session.query(Tweet).\
				filter(Tweet.dataset_id==twitter_id)
	tweet_list = []
	tweet_dict = {}
	for t in tquery.all():
		tweet_list.append(t.native_tweet_id)
		tweet_dict[t.native_tweet_id] = t.tweet_id
		if (t.in_reply_to_native_tweet_id not in tweet_dict
			and t.in_reply_to_native_tweet_id != None):
			tweet_dict[t.in_reply_to_native_tweet_id] = t.in_reply_to_tweet_id
	return tweet_list, tweet_dict

def getHashtagRelationCount(session):
	hrquery = session.query(HashtagRelation).\
				filter(HashtagRelation.dataset_id==twitter_id).count()
	return hrquery

def getUserMentionCount(session):
	umquery = session.query(UserMention).\
				filter(UserMention.dataset_id==twitter_id).count()
	return umquery


####################
# Table Insertions #
####################

# add all table entries to the sqlalchemy session
def createTableObjects(jObj,session):
	addHashtagsToSession(jObj,session)
	addTextToSession(jObj,session)
	addAuthorToSession(jObj,session)
	addTweetToSession(jObj,session)
	addUserMentionToSession(jObj,session)
	addHashtagRelationToSession(jObj,session)

# add hashtags if not already in the database
def addHashtagsToSession(jObj,session):
	hashtags = jObj['entities']['hashtags']
	jObj['iac_hashtag_ids'] = []
	for h in hashtags:
		hText = h['text']
		if hText not in hashtag_dict:
			hashtag_dict[hText] = hashtag_inc.inc()
			hashtag = Hashtag(
				dataset_id 		= twitter_id,
				hashtag_id 		= hashtag_dict[hText],
				hashtag_text 	= hText
				)
			session.add(hashtag)
		jObj['iac_hashtag_ids'].append(hashtag_dict[hText])

# add author only if not already in db
def addAuthorToSession(jObj,session):
	username = jObj['user']['screen_name']
	favorites = jObj['user']['favourites_count']
	followers = jObj['user']['followers_count']
	if username not in author_dict:
		author_dict[username] = author_inc.inc()
		author = Author(
			dataset_id 			= twitter_id,
			author_id 			= author_dict[username],
			username 			= username,
			twitter_followers 	= followers,
			twitter_favorites	= favorites
			)
		session.add(author)
	jObj['iac_author_id'] = author_dict[username]

def addTextToSession(jObj,session):
	t_text = jObj['text']
	tweet_id = tweet_inc.inc()
	text_id = tweet_id
	jObj['iac_tweet_id'] = tweet_id
	text = Text(
		dataset_id 		= twitter_id,
		text_id 		= text_id,
		text 			= t_text
		)
	session.add(text)
	jObj['iac_text_id'] = text_id

def addTweetToSession(jObj,session):
	tweet_id = jObj['iac_text_id'] 
	timestamp = time.strftime('%Y-%m-%d %H:%M:%S', 
		time.strptime(jObj['created_at'],
		'%a %b %d %H:%M:%S +0000 %Y'))

	if jObj['in_reply_to_user_id'] in author_dict:
		reply_author_id = author_dict[jObj['in_reply_to_screen_name']]
	else:
		reply_author_id = None

	if (jObj['in_reply_to_status_id_str'] not in tweet_dict 
		and jObj['in_reply_to_status_id_str'] != None):
		tweet_dict[jObj['in_reply_to_status_id_str']] = tweet_inc.inc()
	else:
		tweet_dict[jObj['in_reply_to_status_id_str']] = None
	reply_tweet_id = tweet_dict[jObj['in_reply_to_status_id_str']]

	if jObj['id_str'] not in tweet_list:
		tweet = Tweet(
			dataset_id 					= twitter_id,
			tweet_id 					= tweet_id,
			author_id 					= jObj['iac_author_id'],
			timestamp 					= timestamp,
			in_reply_to_author_id		= reply_author_id,
			in_reply_to_tweet_id 		= reply_tweet_id,
			in_reply_to_native_tweet_id = jObj['in_reply_to_status_id_str'],
			native_tweet_id 			= jObj['id_str'],
			text_id 					= jObj['iac_text_id'],
			retweets 					= jObj['retweet_count'],
			favorites 					= jObj['favorite_count']
			)
		tweet_list.append(jObj['id_str'])
		if jObj['id_str'] not in tweet_dict:
			tweet_dict[jObj['id_str']] = tweet_id
		session.add(tweet)

# link up tweets to users mentioned in the tweet
# also insert any users that are not in the database
def addUserMentionToSession(jObj,session):
	userMentions = jObj['entities']['user_mentions']
	for user in userMentions:
		if user['screen_name'] not in author_dict:
			author_dict[user['screen_name']] = author_inc.inc()
			# if the username is not in the database
			# we have limited information, but need to insert anyways
			# so the users_mentioned table doesn't give an error
			author = Author(
				dataset_id 			= twitter_id,
				author_id 			= author_dict[user['screen_name']],
				username 			= user['screen_name'],
				# no info for twitter followers or favorites
				twitter_followers 	= None,
				twitter_favorites	= None
				)
			session.add(author)
		userMention = UserMention(
			dataset_id 			= twitter_id,
			user_mention_id 	= user_mention_inc.inc(),
			tweet_id 			= jObj['iac_tweet_id'],
			author_id 			= author_dict[user['screen_name']],
			)
		session.add(userMention)

def addHashtagRelationToSession(jObj,session):
	hashtags = jObj['entities']['hashtags']
	for h in hashtags:
		hashtagRelation = HashtagRelation(
			dataset_id 			= twitter_id,
			hashtag_relation_id	= hashtag_relation_inc.inc(),
			tweet_id 			= jObj['iac_tweet_id'],
			hashtag_id 			= hashtag_dict[h['text']]
			)
		session.add(hashtagRelation)

def main(user=sys.argv[1],pword=sys.argv[2],db=sys.argv[3],dataFile=sys.argv[4]):

	# if len(sys.argv) != 5:
	# 	print("Incorrect number of arguments given")
	# 	print("Usage: python getRawJSON [username] [password] [host/database name] [JSON data file]")
	# 	print("Example: python getRawJSON root password localhost/iac sampleComments")
	# 	sys.exit(1)

	# sqlalchemy magic
	print('Connecting to database',db,'as user',user)
	eng = connect(user, pword, db)
	metadata = s.MetaData(bind=eng)
	session = createSession(eng)
	generateTableClasses(eng)
	# make sure we're not inserting any duplicate entries from another query
	print('loading author, hashtag information from database')
	global author_dict, hashtag_dict, tweet_list, tweet_dict
	author_dict = getAuthorsFromDatabase(session)
	hashtag_dict = getHashtagsFromDatabase(session)
	tweet_list, tweet_dict = getTweetsFromDatabase(session)
	hr_count = getHashtagRelationCount(session)
	um_count = getUserMentionCount(session)
	generateIncrementers(tweet_dict,author_dict,hashtag_dict,hr_count,um_count)
	# run line-by-line through dataFile (to deal with multi-GB files)
	print('Loading data from',dataFile)
	with open(dataFile,'r', encoding='utf-8') as data:
		jObjs = []
		comment_index = 1
		for line in data:
			jObj = jsonLineToDict(line)
			jObjs.append(jObj)
			# every [batch_size] comments, add to DB
			if len(jObjs) >= batch_size:
				for jObj in jObjs:
					# this adds each table entry to the session
					createTableObjects(jObj,session)
				print("Pushing comments up to",comment_index)
				sys.stdout.flush()
				# make sure the script doesn't stop just for an OurSQL warning
				# try:
				# 	session.commit()
				# except Exception as e:
				# 	print("Error:",e)
				session.commit()
				jObjs = []
			comment_index += 1
		# the stragglers
		for jObj in jObjs:
			createTableObjects(jObj,session)
		session.commit()

if __name__ == "__main__":
	main()
