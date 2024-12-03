from pymongo import MongoClient
import certifi

class DatabaseManager:
    def __init__(self, db_uri, database_name, collection_name):
        """
        Initialize the DatabaseManager with MongoDB connection details.
        """
        self.uri = db_uri
        self.database_name = database_name
        self.collection_name = collection_name

    def get_resume(self, username):
        """
        Retrieve the resume for a specific username.
        """
        with MongoClient(self.uri, tlsCAFile=certifi.where()) as client:
            db = client[self.database_name]
            collection = db[self.collection_name]
            user = collection.find_one({'username': username})
            return user.get('data') if user else None

    def save_resume(self, username, resume_data):
        """
        Save or update a resume for a specific username.
        """
        with MongoClient(self.uri, tlsCAFile=certifi.where()) as client:
            db = client[self.database_name]
            collection = db[self.collection_name]
            collection.update_one(
                {'username': username},
                {'$set': {'data': resume_data}},
                upsert=True
            )
