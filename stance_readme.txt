For Amita & others:

To get new tweets based on a search query:
    - change queriesFolder in searchTwitterCL_stance.py (make sure you do this in listJSONtoMySQL.py too)
    - run like so:
        python3 searchTwitterCL_stance.py 'query1' '#query2' 'query 3'
    - script should output a folder inside the queriesFolder you specified with the raw JSON for 18,000 tweets per query
    - need to wait 15 mins between queries because of rate limiting

To upload tweets to the database:
    - make sure your queriesFolder in the script is the same as searchTwitterCL_stance.py
    - run like so:
        python3 listJSONtoMySQL.py (username) (password) (host/database)
    - will extract info for for each raw JSON tweet in the queries folder and insert a the corresponding objects into the database

NOTE: 'topic' field has not yet been added to the database, or to listJSONtoMySQL.py, so don't upload anything yet.
