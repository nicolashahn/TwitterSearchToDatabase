# NLDS Lab
# Nicolas Hahn
# Search Twitter using their search API
# Download tweets to given output file

# -*- coding: utf-8 -*-

from twitter import *
from urllib.parse import quote_plus
from settings import token, token_key, con_secret, con_secret_key
from getpass import getpass

# prepend this to every search call
search_url = "https://api.twitter.com/1.1/search/tweets.json"

# t = Twitter(auth=OAuth(token, token_key, con_secret, con_secret_key))



def main():

	username = input("Enter your username:")
	password = getpass("Enter your password:")

	out_file_name = input("Enter a name for the output file:")
	output = open(out_file_name, 'w')

	n = input("Enter number of search queries: ")
	queries = []
	for i in range(int(n)):
		queries.append(input("Enter query: "))
	print(queries)

	for q in queries:
		url = search_url+quote_plus(q)
		print(url)


if __name__ == "__main__":
	main()
