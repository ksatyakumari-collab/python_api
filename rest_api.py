

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

# Create database
db_new = client["user_db"]

# Create collection
users = db_new["users"]
login_users = db['users']


@app.route('/validate', methods=['GET','POST'])
def validate():
    count = users.count_documents({})

    print("total login users :", count)

    if count == 0:


        return jsonify({
            "message": "no records ",
            "timestamp": datetime.now(timezone.utc),
            "inserted_id": str(result.inserted_id)
        })



    data_user = request.args.to_dict()

    new_user = data_user.get("username")
    Password =data_user.get("Password")
    len = users.count_documents({"username":new_user,
                                 "Password":Password })
  
    if(len>0):
        return jsonify({
                        "message": "validation successful",
                        "timestamp": datetime.now(timezone.utc),

                    })


    return jsonify({
                    "message": "wrong username or password",
                    "timestamp": datetime.now(timezone.utc),

                })

    





@app.route('/users', methods=['GET','POST'])
def add_user():
    count = users.count_documents({})

    print("total login users :", count)

    if count == 0:

        data_user = request.args.to_dict()

        data_user.update({"timestamp": datetime.now(timezone.utc)})

        result = users.insert_one(data_user)

        return jsonify({
            "message": "User added",
            "timestamp": datetime.now(timezone.utc),
            "inserted_id": str(result.inserted_id)
        })


    data_user = request.args.to_dict()

    new_user = data_user.get("username")

    print ("data_user :", data_user)

    len = users.count_documents({"username":new_user})
  
    if(len>0):
        return jsonify({
                        "message": "User already exists",
                        "timestamp": datetime.now(timezone.utc),

                    })

                  
    
 
    data_user.update({"timestamp": datetime.now(timezone.utc)})

    result = users.insert_one(data_user)

    return jsonify({
        "message": "User added",
        "timestamp": datetime.now(timezone.utc),
        "inserted_id": str(result.inserted_id)
    })




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

@app.route('/top_10', methods=['GET'])
def get_top_10():
    try:
        start_time = datetime.now(timezone.utc)
        print("top_10 start time :", start_time)
        result = collection.find(
        {},                      # no filter (all documents)
        {"_id": 1, "likes": 1}   # project only _id and likes
        ).sort("likes", -1).limit(10)

        id_list = []
        likes_list = []
    
        for doc in result:
            doc['_id'] = str(doc['_id'])
            id_list.append(doc['_id'])
            likes_list.append(doc['likes'])            
            print("decending order list :",doc['_id'], doc['likes'])
            
        data = [{"id": t, "likes": c} for t, c in zip(id_list, likes_list)]
        print("top_10 end time :", datetime.now(timezone.utc))
        
        print("top_10 time :", datetime.now(timezone.utc) - start_time)

        return jsonify(data), 500
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
        start_time = end;
        print("recent start time :",start_time)

        # ------------------ HOUR BASED ------------------
        if count_type == 'hour':
            
            end = datetime.now(timezone.utc)
            start = end - timedelta(hours=24)

          
         
            print("recent start time :",start_time)

            # ------------------ HOUR BASED ------------------
            if count_type == 'hour':
                
                end = datetime.now(timezone.utc)    
                start = end - timedelta(hours=24)

                query = {
                    "_id": {
                        "$gte": ObjectId.from_datetime(start),
                        "$lt": ObjectId.from_datetime(end)
                    }
                }
                result = collection.find(query)

                # Prepare last 24 hours slots
                hours = []
                counts = []
                end = datetime.now(timezone.utc)   
                
                for i in range(24):
                    start = end - timedelta(hours=i+1)
                    access = 0
                    collection.find()
                    counts.append(access)
                    hours.append(start.strftime("%H:00"))
                    end =start

                

                data = [{"time": t, "count": c} for t, c in zip(hours, counts)]
                
                   


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

        print("recent end time :", datetime.now(timezone.utc))
        
        print("recent time :", datetime.now(timezone.utc) - start_time)

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
    print("main function call")
    app.run(debug=True)
    

    

