from flask import Flask
from flask import render_template, Response
from havenondemand.hodindex import HODClient
from flask import request
import praw
import json
from domain_fix import crossdomain
from Client import MongoDBClient
import nltk

app = Flask(__name__)

collection = MongoDBClient().get_db().redditComments

try:
    collection.ensure_index([('comment', 'text')])
except Exception:
    pass


def get_adjectives(body):
    poss = nltk.pos_tag(nltk.word_tokenize(body))
    adjectives = []
    for pos in poss:
        if pos[1] in ["JJ", "NN", "WP"]:
            adjectives.append(pos[0])
    return [adjective.lower() for adjective in adjectives]


def word_list_frequency_tuple(word_list):
    frequency_map = nltk.FreqDist(word_list)
    return [[key, value] for key, value in frequency_map.items()]


def search_keyword(keywords):
    keywords = keywords.lower()
    cursor = collection.find()
    relevant = []
    for c in cursor:
        try:
            if c['comment'].lower().find(keywords) != -1:
                relevant.append(c)
        except Exception:
            pass
    return relevant
    # cursor = collection.find({'$text': { '$search': keywords}})
    # return [c for c in cursor]


def search_thread_id(thread_id):
    cursor = collection.find({'thread_id': thread_id})
    return [c["sentiment"] for c in cursor]


def store(comment, thread_id, sentiment):
    collection.insert({"comment": comment, "thread_id": thread_id,
                       "sentiment": sentiment,
                       "adjectives": get_adjectives(comment)})


@app.route('/sentiment/<keyword>')
def get_sentiment_towards_word(keyword):
    related_objects = search_keyword(keyword)
    sentiments = []
    for obj in related_objects:
        try:
            sentiments.append(obj['sentiment'])
        except Exception:
            pass
    return Response(json.dumps(sentiments), mimetype="application/json")


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/word_cloud/<keyword>')
def word_cloud(keyword):
    related_objects = search_keyword(keyword)
    adjectives = []
    for obj in related_objects:
        try:
            # not all will have adjectives
            adjectives.extend(obj['adjectives'])
        except Exception:
            pass
    returned_values = word_list_frequency_tuple(adjectives)
    returned_values.sort(key=lambda x: x[1])
    for value_list in returned_values:
        value_list[1] *= 10
    return Response(json.dumps(returned_values[-1:-11:-1]),
                    mimetype="application/json")


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
    stored_sentiments = search_thread_id(thread)
    if stored_sentiments != []:
        return Response(json.dumps(stored_sentiments),
                        mimetype="application/json")

    # establish client
    client = HODClient(
        "http://api.havenondemand.com", "65f7315d-1189-449f-a839-7a46fd4263be")

    # create the intial user agent
    user_agent = "reddit-mood-analyzer-scrape by /u/abrarisland"
    reddit = praw.Reddit(user_agent=user_agent)

    submission = reddit.get_submission(
        submission_id=thread, comment_limit=15)

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
            insertion_objects.append(
                {"comment": body, "thread_id": thread,
                 "sentiment": sentiment, "adjectives": get_adjectives(body)})
            results.append(sentiment)
    collection.insert_many(insertion_objects)

    # store json formatted text in output
    return Response(json.dumps(results), mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
