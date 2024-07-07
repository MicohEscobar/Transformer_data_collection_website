import pandas as pd
from pymongo import MongoClient
from bson import ObjectId

# MongoDB Atlas connection string
mongo_uri = "mongodb+srv://micoh:englich@3scobar.uzdzj3q.mongodb.net/"
client = MongoClient(mongo_uri)
db = client['englich']
collection = db['output_1']

# Read the CSV file
csv_file = '/home/micoh/flask/datacollectionsite/csvs/output_2.csv'
df = pd.read_csv(csv_file)



df.columns = ['english']

df['chichewa'] = ""



# Function to format the data
def format_data(row):
    return {
        "_id": ObjectId(),  # Auto-generate ObjectId
        "english": row['english'],
        "chichewa": row['chichewa']
    }

# Prepare data for insertion
data = df.apply(format_data, axis=1).tolist()

# Insert data into MongoDB
result = collection.insert_many(data)
print(f"Inserted {len(result.inserted_ids)} documents.")

print("Data upload complete.")