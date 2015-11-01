from flask import Flask
from flask import jsonify, render_template, Response
from havenondemand.hodindex import HODClient
from flask import request
from pymongo import MongoClient
import praw
import json
from domain_fix import crossdomain
from Client import MongoDBClient
import datetime
import nltk

app = Flask(__name__)

collection = MongoDBClient().get_db().redditComments

def getAdjectives(body):
    poss = nltk.pos_tag(nltk.word_tokenize(body))
    adjectives = []    
    for pos in poss:
        if pos[1] in ["JJ", "NN", "WP"]:
            adjectives.append(pos[0])
    return [adjective.lower() for adjective in adjectives]

def wordListToFrequencyTuple(word_list):
    frequencyMap = nltk.FreqDist(word_list)
    return [[key, value] for key, value in frequencyMap.items()]

def searchKeyword(keywords):
    collection.ensure_index([('comment', 'text')])
    cursor = collection.find({'$text': { '$search': keywords}})
    return [c for c in cursor]

def searchThreadId(threadId):
    collection = MongoDBClient().get_db().redditComments
    cursor = collection.find({'threadId':threadId})
    return [c for c in cursor]
    
def store(comment, threadId, sentiment):
    collection.insert({"comment":comment, "threadId":threadId, "sentiment":sentiment, "adjectives":getAdjectives(comment)})

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/report.html")
@app.route("/report/<topic>")
def report(topic=None):
    if topic is None:        
        topic = request.args.get('topic')
    return render_template("report.html", topic=topic)


@app.route("/<subreddit>/<thread>")
@crossdomain(origin="*")
def r(subreddit, thread):


    # if db has stored values, return stored values
    stored_sentiments = searchThreadID(thread)
    if stored_sentiments != []:
        return Response(jsons.dumps(stored_sentiments), mimetype="application/json")

    # establish client
    client = HODClient(
        "http://api.havenondemand.com", "65f7315d-1189-449f-a839-7a46fd4263be")

    # create the intial user agent
    user_agent = "reddit-mood-analyzer-scrape by /u/abrarisland"
    reddit = praw.Reddit(user_agent=user_agent)

    submission = reddit.get_submission(submission_id=thread, comment_limit=15)

    # get all of the comments in the thread and flatten the comment tree
    flat_comments = praw.helpers.flatten_tree(submission.comments)

    results = []
    insertion_objects = []

    for comment in flat_comments:
        if isinstance(comment, praw.objects.MoreComments):
            continue
        body = comment.body
        if body != "[deleted]":
            r = client.post('analyzesentiment', {'text': body})
            output = r.json()
            sentiment = output["aggregate"]["score"]
            insertion_objects.append({"comment":body, "threadId":thread, "sentiment":sentiment, "adjectives":getAdjectives(body)})
            results.append(sentiment)
    collection.insert_many(insertion_objects)

    # store json formatted text in output
    return Response(json.dumps(results), mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
