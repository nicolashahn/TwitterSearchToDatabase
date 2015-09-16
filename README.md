# Twitter Search To Database

Given a search query, download a certain amount of tweets that fit that query, and then upload them to the IAC database.
```
twitterSearch.py
```
- Takes multiple search queries from the user
- Dumps them in JSON format into individual output files
```
twitterJSONtoMySQL.py <username> <password> <host/db> <query_file>
```
- Takes these JSON dump files, inserts them into database
```
twitterStructure.sql
```
- Updates IAC to allow for Twitter data
- Run this before using twitterJSONtoMySQL.py
