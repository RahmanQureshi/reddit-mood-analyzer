class MongoDBClient(object):
    """ Used to set config information about the database and store
    private collection information. """

    def __init__(self):
        import pymongo
        import os
        import re
        pattern = r'^mongodb\:\/\/((?P<username>[_\w]+):(?P<password>[\w]+)@)?(?P<host>[\.\w]+):(?P<port>\d+)/(?P<database>[_\w]+)$'
        try:
            mongolab_uri = os.environ['MONGOLAB_URI']
        except KeyError:
            mongolab_uri = 'mongodb://localhost:27017/test'
        data = re.search(pattern, mongolab_uri).groupdict()
        client = pymongo.MongoClient(mongolab_uri)
        self.db = client.get_database(data['database'])

    def get_db(self):
        return self.db
