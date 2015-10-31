import praw

# create the intial user agent
user_agent = "reddit-mood-analyzer-scrape by /u/abrarisland"
reddit = praw.Reddit(user_agent=user_agent)

# original submissions info is a generator object
submissions = reddit.get_subreddit("uoft").get_top(limit=5)
for thread in submissions:

	# get all of the comments in the thread and flatten the comment tree
	thread.replace_more_comments(limit=None, threshold=0)
	flat_comments = praw.helpers.flatten_tree(thread.comments)
	
	for comment in flat_comments:
		body = comment.body
		if body != "[deleted]":
			print(body)
