from flask import request, jsonify
from database import mongo
from config import JWT_SECRET
from bson.objectid import ObjectId
import jwt

def get_current_user():
    header = request.headers.get("Authorization")

    if not header:
        return None, jsonify({"error": "Token is required"}), 401

    try:
        token = header.split(" ")[1]
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        user = mongo.db.users.find_one({
            "_id": ObjectId(data["user_id"])
        })

        return user, None, None

    except Exception:
        return None, jsonify({"error": "Invalid token"}), 401
