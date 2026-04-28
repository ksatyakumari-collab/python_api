

from tracemalloc import start

from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta, timezone
from flask_cors import CORS, cross_origin
import webbrowser
import os
import requests

ENDPOINT = "http://127.0.0.1:5000"

app = Flask(__name__)
CORS(app, support_credentials=True)
@cross_origin(supports_credentials=True)

@app.route('/api/hello_api',methods=['GET'])
def hello():
    return jsonify("message=Hello world restapi"),200

# MongoDB connection
client = MongoClient('mongodb+srv://talashdrive:talashdrive@cluster1.7xzdzgk.mongodb.net/', serverSelectionTimeoutMS=1000)
db = client['ample_mflix']
collection = db['playlists']

@app.route('/health', methods=['GET'])
def health_check():
    try:
        client.admin.command('ping')
        return jsonify({"status": "MongoDB is connected"}), 200
    except Exception as e:
        return jsonify({"status": "Connection failed", "error": str(e)}), 500

@app.route('/count', methods=['GET'])
def get_count():
    try:
        count = collection.count_documents({})
        return jsonify({"total_documents": count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/count/recent', methods=['GET'])
def get_recent_count():
    try:
        count_type = request.args.get('type')

        #count_type = request.args.get('type', 'hour')  # default = hour

        num_access = []
        time_labels = []

        end = datetime.now(timezone.utc)

        # ------------------ HOUR BASED ------------------
        if count_type == 'hour':
            for i in range(24):
                start = end - timedelta(hours=1)

                query = {
                    "_id": {
                        "$gte": ObjectId.from_datetime(start),
                        "$lt": ObjectId.from_datetime(end)
                    }
                }

                count = collection.count_documents(query)

                time_labels.append(start.strftime("%H:%M"))
                num_access.append(count)

                end = start  # move window backward

        # ------------------ DAY BASED ------------------
        elif count_type == 'day':
            for i in range(7):  # last 7 days (you can change)
                start = end - timedelta(days=1)

                query = {
                    "_id": {
                        "$gte": ObjectId.from_datetime(start),
                        "$lt": ObjectId.from_datetime(end)
                    }
                }

                count = collection.count_documents(query)

                time_labels.append(start.strftime("%Y-%m-%d"))
                num_access.append(count)

                end = start

        else:
            return jsonify({"error": "Invalid type. Use 'hour' or 'day'"}), 400

        # ------------------ FINAL RESPONSE ------------------
        data = [{"time": t, "count": c} for t, c in zip(time_labels, num_access)]

        return jsonify({"data": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/document/<id>', methods=['GET'])
def get_document(id):
    try:
        document_id = ObjectId(id)
        document = collection.find_one({"_id": document_id})
        if document:
            # Convert ObjectId to string for JSON serialization
            document['_id'] = str(document['_id'])
            return jsonify(document), 200
        else:
            return jsonify({"error": "Document not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        limit = int(request.args.get('limit', 10))
        documents = list(collection.find().limit(limit))
        for doc in documents:
            doc['_id'] = str(doc['_id'])
        return jsonify(documents),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    
    app.run(debug=True)
    

    

