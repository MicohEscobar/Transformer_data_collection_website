from pymongo import MongoClient

# MongoDB Atlas connection string
mongo_uri = "mongodb+srv://micoh:englich@3scobar.uzdzj3q.mongodb.net/"
client = MongoClient(mongo_uri)

# Database and collection
db = client['englich']
collection = db['output_1']

# Test the connection
try:
    # Print out one document to verify the connection
    document = collection.find_one()
    print(f"Connected to MongoDB Atlas. First document: {document}")
except Exception as e:
    print(f"Error: {e}")
