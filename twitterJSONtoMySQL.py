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
import datetime

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
post_dict = {}

# temporary output file for checking things 
# (print statements choke on unicode)
tempOut = open('tempOut','w', encoding='utf-8')


###################################
# Sample Tweet JSON
###################################

# {  
#    'truncated':False,
#    'user':{  
#       'favourites_count':46,
#       'location':'',
#       'profile_sidebar_fill_color':'DDEEF6',
#       'protected':False,
#       'following':False,
#       'profile_sidebar_border_color':'C0DEED',
#       'is_translator':False,
#       'follow_request_sent':False,
#       'default_profile':True,
#       'profile_banner_url':'https://pbs.twimg.com/profile_banners/3023737407/1436502409',
#       'profile_background_tile':False,
#       'notifications':False,
#       'profile_text_color':'333333',
#       'has_extended_profile':False,
#       'time_zone':None,
#       'url':'http://t.co/Iv8P3dADr7',
#       'followers_count':26,
#       'contributors_enabled':False,
#       'name':"Popoola Shu'ayb",
#       'entities':{  
#          'description':{  
#             'urls':[  

#             ]
#          },
#          'url':{  
#             'urls':[  
#                {  
#                   'display_url':'aiqingltd.com',
#                   'expanded_url':'http://www.aiqingltd.com',
#                   'indices':[  
#                      0,
#                      22
#                   ],
#                   'url':'http://t.co/Iv8P3dADr7'
#                }
#             ]
#          }
#       },
#       'profile_link_color':'0084B4',
#       'profile_background_image_url':'http://abs.twimg.com/images/themes/theme1/bg.png',
#       'lang':'en',
#       'description':'',
#       'profile_background_image_url_https':'https://abs.twimg.com/images/themes/theme1/bg.png',
#       'statuses_count':707,
#       'profile_image_url':'http://pbs.twimg.com/profile_images/619374493333651456/B4njnXR4_normal.jpg',
#       'friends_count':41,
#       'profile_image_url_https':'https://pbs.twimg.com/profile_images/619374493333651456/B4njnXR4_normal.jpg',
#       'listed_count':17,
#       'profile_use_background_image':True,
#       'profile_background_color':'C0DEED',
#       'utc_offset':None,
#       'id':3023737407,
#       'default_profile_image':False,
#       'geo_enabled':False,
#       'is_translation_enabled':False,
#       'verified':False,
#       'screen_name':'abu_fawziyyah',
#       'created_at':'Sat Feb 07 19:49:18 +0000 2015',
#       'id_str':'3023737407'
#    },
#    'retweet_count':3,
#    'in_reply_to_status_id_str':None,
#    'is_quote_status':False,
#    'geo':None,
#    'in_reply_to_screen_name':None,
#    'lang':'en',
#    'entities':{  
#       'user_mentions':[  
#          {  
#             'name':'Microsoft Education',
#             'screen_name':'Microsoft_EDU',
#             'id':17826187,
#             'id_str':'17826187',
#             'indices':[  
#                3,
#                17
#             ]
#          },
#          {  
#             'name':'SADA Systems',
#             'screen_name':'SADASystems',
#             'id':102541572,
#             'id_str':'102541572',
#             'indices':[  
#                38,
#                50
#             ]
#          },
#          {  
#             'name':'Microsoft',
#             'screen_name':'Microsoft',
#             'id':74286565,
#             'id_str':'74286565',
#             'indices':[  
#                57,
#                67
#             ]
#          }
#       ],
#       'urls':[  
#          {  
#             'display_url':'msft.it/6018BHehi',
#             'expanded_url':'http://msft.it/6018BHehi',
#             'indices':[  
#                111,
#                133
#             ],
#             'url':'http://t.co/Soq7NHEkc7'
#          }
#       ],
#       'symbols':[  

#       ],
#       'hashtags':[  
#          {  
#             'text':'Cloud',
#             'indices':[  
#                83,
#                89
#             ]
#          },
#          {  
#             'text':'MSFTEDU',
#             'indices':[  
#                134,
#                140
#             ]
#          }
#       ]
#    },
#    'source':'<a href="http://blackberry.com/twitter" rel="nofollow">Twitter for BlackBerry®</a>',
#    'retweeted':False,
#    'text':'RT @Microsoft_EDU: Congratulations to @SADASystems, 2015 @Microsoft U.S. Education #Cloud Partner of the Year: http://t.co/Soq7NHEkc7 #MSFT…',
#    'favorite_count':0,
#    'in_reply_to_user_id_str':None,
#    'retweeted_status':{  
#       'truncated':False,
#       'user':{  
#          'favourites_count':336,
#          'location':'Redmond, WA',
#          'profile_sidebar_fill_color':'DDEEF6',
#          'protected':False,
#          'following':False,
#          'profile_sidebar_border_color':'FFFFFF',
#          'is_translator':False,
#          'follow_request_sent':False,
#          'default_profile':False,
#          'profile_banner_url':'https://pbs.twimg.com/profile_banners/17826187/1433435092',
#          'profile_background_tile':False,
#          'notifications':False,
#          'profile_text_color':'333333',
#          'has_extended_profile':False,
#          'time_zone':'Pacific Time (US & Canada)',
#          'url':'http://t.co/7FJ4W59tTX',
#          'followers_count':120538,
#          'contributors_enabled':False,
#          'name':'Microsoft Education',
#          'entities':{  
#             'description':{  
#                'urls':[  

#                ]
#             },
#             'url':{  
#                'urls':[  
#                   {  
#                      'display_url':'microsoft.com/education',
#                      'expanded_url':'http://www.microsoft.com/education',
#                      'indices':[  
#                         0,
#                         22
#                      ],
#                      'url':'http://t.co/7FJ4W59tTX'
#                   }
#                ]
#             }
#          },
#          'profile_link_color':'0084B4',
#          'profile_background_image_url':'http://pbs.twimg.com/profile_background_images/461932094302605312/4PbCjFqM.jpeg',
#          'lang':'en',
#          'description':'Discovering, highlighting and enabling innovation and achievement among students, teachers and schools',
#          'profile_background_image_url_https':'https://pbs.twimg.com/profile_background_images/461932094302605312/4PbCjFqM.jpeg',
#          'statuses_count':8437,
#          'profile_image_url':'http://pbs.twimg.com/profile_images/378800000365876375/29ada37d90cbcebe4772acbbfb244b5f_normal.jpeg',
#          'friends_count':4919,
#          'profile_image_url_https':'https://pbs.twimg.com/profile_images/378800000365876375/29ada37d90cbcebe4772acbbfb244b5f_normal.jpeg',
#          'listed_count':2135,
#          'profile_use_background_image':False,
#          'profile_background_color':'61C4F2',
#          'utc_offset':-25200,
#          'id':17826187,
#          'default_profile_image':False,
#          'geo_enabled':False,
#          'is_translation_enabled':False,
#          'verified':False,
#          'screen_name':'Microsoft_EDU',
#          'created_at':'Wed Dec 03 02:29:33 +0000 2008',
#          'id_str':'17826187'
#       },
#       'retweet_count':3,
#       'in_reply_to_status_id_str':None,
#       'is_quote_status':False,
#       'geo':None,
#       'in_reply_to_screen_name':None,
#       'lang':'en',
#       'entities':{  
#          'user_mentions':[  
#             {  
#                'name':'SADA Systems',
#                'screen_name':'SADASystems',
#                'id':102541572,
#                'id_str':'102541572',
#                'indices':[  
#                   19,
#                   31
#                ]
#             },
#             {  
#                'name':'Microsoft',
#                'screen_name':'Microsoft',
#                'id':74286565,
#                'id_str':'74286565',
#                'indices':[  
#                   38,
#                   48
#                ]
#             }
#          ],
#          'urls':[  
#             {  
#                'display_url':'msft.it/6018BHehi',
#                'expanded_url':'http://msft.it/6018BHehi',
#                'indices':[  
#                   92,
#                   114
#                ],
#                'url':'http://t.co/Soq7NHEkc7'
#             }
#          ],
#          'symbols':[  

#          ],
#          'hashtags':[  
#             {  
#                'text':'Cloud',
#                'indices':[  
#                   64,
#                   70
#                ]
#             },
#             {  
#                'text':'MSFTEDU',
#                'indices':[  
#                   115,
#                   123
#                ]
#             }
#          ]
#       },
#       'source':'<a href="http://www.sprinklr.com" rel="nofollow">Sprinklr</a>',
#       'retweeted':False,
#       'text':'Congratulations to @SADASystems, 2015 @Microsoft U.S. Education #Cloud Partner of the Year: http://t.co/Soq7NHEkc7 #MSFTEDU',
#       'favorite_count':4,
#       'in_reply_to_user_id_str':None,
#       'metadata':{  
#          'iso_language_code':'en',
#          'result_type':'recent'
#       },
#       'place':None,
#       'in_reply_to_user_id':None,
#       'id':636648563532038144,
#       'in_reply_to_status_id':None,
#       'possibly_sensitive':False,
#       'favorited':False,
#       'created_at':'Wed Aug 26 21:17:00 +0000 2015',
#       'id_str':'636648563532038144',
#       'coordinates':None,
#       'contributors':None
#    },
#    'metadata':{  
#       'iso_language_code':'en',
#       'result_type':'recent'
#    },
#    'place':None,
#    'in_reply_to_user_id':None,
#    'id':636654391240605700,
#    'in_reply_to_status_id':None,
#    'possibly_sensitive':False,
#    'favorited':False,
#    'created_at':'Wed Aug 26 21:40:09 +0000 2015',
#    'id_str':'636654391240605700',
#    'coordinates':None,
#    'contributors':None
# }


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
	# let HashtagRelation auto increment in MySQL
	global post_inc, author_inc, hashtag_inc, user_mention_inc

	# TODO: put incrementers, ABase classes in
	# query db at start of script to see how many are already in there
	tweet_inc = Incrementer()
	author_inc = Incrementer()
	text_inc = Incrementer()
	hashtag_inc = Incrementer()
	# hashtag_relation auto increments
	user_mention_inc = Incrementer()

	Tweet = ABase.classes.tweets 
	Author = ABase.classes.authors 
	Text = ABase.classes.texts 
	Hashtag = ABase.classes.hashtags 
	HashtagRelation = ABase.classes.hashtag_relations
	UserMention = ABase.classes.user_mentions



###################################
# Table Insertions
###################################

# add all table entries to the sqlalchemy session
def createTableObjects(jObj,session):
	addHashtagsToSession(jObj,session)
	addTextToSession(jObj,session)
	addAuthorToSession(jObj,session)
	addUserMentionToSession(jObj,session)
	addTweetToSession(jObj,session)

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
			hashtag_id 		= hashtag_dict[hText]
			hashtag_text 	= hText
			)
		session.add(hashtag)
		jObj['iac_hashtag_ids'].append(hashtag_dict[hText])

def addTextToSession(jObj,session):
	tText = jObj['text']
	tId = text_inc.inc()
	text = Text(
		dataset_id 		= twitter_id,
		text_id 		= tId,
		text 			= tText
		)
	session.add(text)
	jObj['iac_text_id'] = text_inc.inc()

# add author if not already in db
def addAuthorToSession(jObj,session):
	username = jObj['user']['screen_name']
	if username not in author_dict:
		author_dict[username] = author_inc.inc()
		author = Author(
			dataset_id 		= twitter_id,
			author_id 		= author_dict[username],
			username 		= username
			)
		session.add(author)

def addUserMentionToSession(jObj,session):
	pass

def addTweetToSession(jObj,session):
	pass

def addHashtagRelationToSession(jObj,session):
	pass



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
				try:
					session.commit()
				except Exception:
					pass
				jObjs = []
			comment_index += 1
		session.commit()

if __name__ == "__main__":
	main()
