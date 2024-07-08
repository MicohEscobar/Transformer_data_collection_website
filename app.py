import os
from flask import Flask, render_template, jsonify, request
# from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS
from googletrans import Translator
from bson import ObjectId

app = Flask(__name__)
load_dotenv()
CORS(app)

def index():
    # Accessing the X-Real-IP header to get the client's real IP address
    real_ip = request.headers.get('X-Real-IP', request.remote_addr)

# MongoDB Atlas connection string
mongo_uri = os.getenv('MONGO_URL')
client = MongoClient(mongo_uri, server_api=ServerApi('1'))
db = client['englich']
collection = db['output_1']

translator = Translator()

# Function to retrieve a single untranslated sentence from MongoDB
def get_untranslated_sentence_from_mongodb(offset):
    try:
        sentences = collection.find({"$or": [{"Chichewa": None}, {"Chichewa": ""}]}).skip(offset).limit(1)
        sentence = next(sentences, None)
        return sentence
    except Exception as err:
        print(f"Error: {err}")
        return None

# Function to translate a sentence
def translate_sentence(sentence, src_language='en', dest_language='ny'):
    try:
        translation = translator.translate(sentence, src=src_language, dest=dest_language)
        return translation.text
    except Exception as e:
        print(f"Translation failed for '{sentence}': {e}")
        return None

# Route to display the initial page
@app.route('/')
def index():
    return render_template('index.html')

# Route to fetch the next sentence
@app.route('/next_sentence/<int:offset>', methods=['GET'])
def next_sentence(offset):
    sentence = get_untranslated_sentence_from_mongodb(offset)
    if sentence:
        sentence_id, english_text = sentence['_id'], sentence['english']
        translated_sentence = translate_sentence(english_text, src_language='en', dest_language='ny')  # Translate to Chichewa
        result = {'id': str(sentence_id), 'english': english_text, 'chichewa': translated_sentence}
    else:
        result = None
    return jsonify(result=result)

# Route to submit the edited Chichewa sentence
@app.route('/submit_translation', methods=['POST'])
def submit_translation():
    data = request.json
    sentence_id = data['id']
    chichewa_text = data['chichewa']
    try:
        # Debugging: Print the ID and translated text
        print(f"Updating document with ID: {sentence_id}, Chichewa: {chichewa_text}")

        # Ensure we use ObjectId for the MongoDB update
        result = collection.update_one({'_id': ObjectId(sentence_id)}, {"$set": {'Chichewa': chichewa_text}})

        # Debugging: Print the result of the update operation
        print(f"Matched {result.matched_count} document(s), Modified {result.modified_count} document(s)")

        if result.modified_count > 0:
            return jsonify(success=True)
        else:
            return jsonify(success=False, message="No documents were updated.")
    except Exception as err:
        print(f"Error: {err}")
        return jsonify(success=False, message=str(err))

if __name__ == '__main__':
    app.run(debug=True)

