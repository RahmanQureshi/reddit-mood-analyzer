from haveondemand.hodindex import HODClient

# establish client
client = HODClient("http://api.havenondemand.com", "65f7315d-1189-449f-a839-7a46fd4263be")

query = 'I like reddit, let us analyze some posts!'
# POST request from client
r = client.post('analyzesentiment', {'text': query})
# store json formatted text in output
output = r.json()

