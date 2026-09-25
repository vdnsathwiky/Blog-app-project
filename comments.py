from flask import Blueprint, request, jsonify
from database import mongo
from middleware import get_current_user
from bson.objectid import ObjectId
from datetime import datetime

comments_bp = Blueprint("comments", __name__)

@comments_bp.route("/blogs/<blog_id>/comments", methods=["GET"])
def get_comments(blog_id):
    try:
        blog = mongo.db.blogs.find_one({"_id": ObjectId(blog_id)})
    except Exception:
        return jsonify({"error": "Invalid blog ID"}), 400

    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    comments = list(
        mongo.db.comments.find({"blog_id": blog_id}).sort("created_at", -1)
    )

    result = []

    for comment in comments:
        result.append({
            "id": str(comment["_id"]),
            "user_id": comment["user_id"],
            "comment": comment["comment"],
            "created_at": comment["created_at"]
        })

    return jsonify({"comments": result}), 200

@comments_bp.route("/blogs/<blog_id>/comments", methods=["POST"])
def add_comment(blog_id):
    user, error, code = get_current_user()
    if error:
        return error, code

    try:
        blog = mongo.db.blogs.find_one({"_id": ObjectId(blog_id)})
    except Exception:
        return jsonify({"error": "Invalid blog ID"}), 400

    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    if blog["status"] != "published":
        return jsonify({"error": "Comments are allowed only on published blogs"}), 400

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    comment_text = data.get("comment", "").strip()

    if not comment_text:
        return jsonify({"error": "comment is required"}), 400

    comment = {
        "blog_id": blog_id,
        "user_id": str(user["_id"]),
        "comment": comment_text,
        "created_at": datetime.utcnow()
    }

    result = mongo.db.comments.insert_one(comment)

    return jsonify({
        "message": "Comment added successfully",
        "comment_id": str(result.inserted_id)
    }), 201
