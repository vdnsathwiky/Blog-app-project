from flask import Blueprint, request, jsonify
from database import mongo
from config import JWT_SECRET
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta ,timezone
import jwt

auth_bp = Blueprint("auth", __name__)

def create_token(user_id):
    data = {
        "user_id": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    return jwt.encode(data, JWT_SECRET, algorithm="HS256")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if "@" not in email:
        return jsonify({"error": "Enter a valid email"}), 400

    if mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    user = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "role": "user",
        "created_at": datetime.now(timezone.utc)
    }

    result = mongo.db.users.insert_one(user)

    return jsonify({
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = mongo.db.users.find_one({"email": email})

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful",
        "token": create_token(user["_id"])
    }), 200
