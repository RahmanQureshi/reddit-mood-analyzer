from flask import Flask
from flask import jsonify, render_template, Response
from havenondemand.hodindex import HODClient
from flask import request
import praw
import json
from domain_fix import crossdomain

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/report.html")
def report():
    topic = request.args.get('topic')
    return topic

@app.route("/<subreddit>/<thread>")
@crossdomain(origin="*")
def r(subreddit, thread):
    # establish client
    client = HODClient(
        "http://api.havenondemand.com", "65f7315d-1189-449f-a839-7a46fd4263be")

    # create the intial user agent
    user_agent = "reddit-mood-analyzer-scrape by /u/abrarisland"
    reddit = praw.Reddit(user_agent=user_agent)

    submission = reddit.get_submission(submission_id=thread, comment_limit =15)

    # get all of the comments in the thread and flatten the comment tree
    flat_comments = praw.helpers.flatten_tree(submission.comments)

    results = []

    for comment in flat_comments:
        if isinstance(comment, praw.objects.MoreComments):
            continue
        body = comment.body
        if body != "[deleted]":
            r = client.post('analyzesentiment', {'text': body})
            output = r.json()
            results.append(output["aggregate"]["score"])

    # store json formatted text in output
    return Response(json.dumps(results), mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
