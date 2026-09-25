from flask import request, jsonify
from database import mongo
from config import JWT_SECRET
from bson.objectid import ObjectId
import jwt

def get_current_user():
    header = request.headers.get("Authorization")

    if not header:
        return None, jsonify({"error": "Authentication token is required"}), 401

    if not header.startswith("Bearer "):
        return None, jsonify({"error": "Use Bearer token"}), 401

    token = header.split(" ", 1)[1]

    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = mongo.db.users.find_one({"_id": ObjectId(data["user_id"])})

        if not user:
            return None, jsonify({"error": "User not found"}), 401

        return user, None, None

    except Exception:
        return None, jsonify({"error": "Invalid or expired token"}), 401
