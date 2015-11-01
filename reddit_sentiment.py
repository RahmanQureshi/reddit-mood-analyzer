from flask import Flask
from flask import jsonify, render_template, Response
from havenondemand.hodindex import HODClient
import praw
import json
from domain_fix import crossdomain


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<subreddit>/<thread>")
@crossdomain(origin="*")
def r(subreddit, thread):
    # establish client
    client = HODClient(
        "http://api.havenondemand.com", "65f7315d-1189-449f-a839-7a46fd4263be")

    # create the intial user agent
    user_agent = "reddit-mood-analyzer-scrape by /u/abrarisland"
    reddit = praw.Reddit(user_agent=user_agent)

    submission = reddit.get_submission(submission_id=thread)

    # get all of the comments in the thread and flatten the comment tree
    submission.replace_more_comments(limit=None, threshold=0)
    flat_comments = praw.helpers.flatten_tree(submission.comments)

    results = []

    for comment in flat_comments:
        body = comment.body
        if body != "[deleted]":
            r = client.post('analyzesentiment', {'text': body})
            output = r.json()
            results.append(output["aggregate"]["score"])

    # store json formatted text in output
    return Response(json.dumps(results), mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
