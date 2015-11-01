from flask import Flask
from flask import jsonify
from flask import render_template
from havenondemand.hodindex import HODClient
from flask import request


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/report.html")
def report():
    topic = request.args.get('topic')
    return topic

@app.route("/r/<subreddit>/<thread>")
def r(subreddit, thread):	
    # establish client
    client = HODClient("http://api.havenondemand.com", "65f7315d-1189-449f-a839-7a46fd4263be")
    
    query = 'I like reddit, let us analyze some posts!'
    # POST request from client
    r = client.post('analyzesentiment', {'text': query})
    # store json formatted text in output
    output = r.json()
    return jsonify(output)

if __name__ == "__main__":
    app.run(debug=True)

