from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from googletrans import Translator
from bson import ObjectId
import os
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# MongoDB Atlas connection string from environment variable
mongo_uri = os.getenv('MONGO_URI', "mongodb+srv://micoh:englich@3scobar.uzdzj3q.mongodb.net/")
try:
    client = MongoClient(mongo_uri)
    db = client['englich']
    collection = db['output_1']
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    db = None

translator = Translator()

# Function to retrieve a single untranslated sentence from MongoDB
def get_untranslated_sentence_from_mongodb(offset):
    try:
        sentences = collection.find({"$or": [{"Chichewa": None}, {"Chichewa": ""}]}).skip(offset).limit(1)
        sentence = next(sentences, None)
        return sentence
    except Exception as err:
        logging.error(f"Error: {err}")
        return None

# Function to translate a sentence
def translate_sentence(sentence, src_language='en', dest_language='ny'):
    try:
        translation = translator.translate(sentence, src=src_language, dest=dest_language)
        return translation.text
    except Exception as e:
        logging.error(f"Translation failed for '{sentence}': {e}")
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
        logging.debug(f"Updating document with ID: {sentence_id}, Chichewa: {chichewa_text}")
        result = collection.update_one({'_id': ObjectId(sentence_id)}, {"$set": {'Chichewa': chichewa_text}})
        logging.debug(f"Matched {result.matched_count} document(s), Modified {result.modified_count} document(s)")
        if result.modified_count > 0:
            return jsonify(success=True)
        else:
            return jsonify(success=False, message="No documents were updated.")
    except Exception as err:
        logging.error(f"Error: {err}")
        return jsonify(success=False, message=str(err))

if __name__ == '__main__':
    app.run(debug=True)
