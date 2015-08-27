# twitterSearch

Given a search query, download a certain amount of tweets that fit that query, and then upload them to the IAC database.
```
twitterSearch.py
```
- Takes multiple search queries from the user
- Dumps them in JSON format into individual output files
```
twitterJSONtoMySQL.py
```
- Takes these JSON dump files, inserts them into IAC database