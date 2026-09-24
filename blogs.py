from flask import Blueprint, request, jsonify
from database import mongo
from middleware import get_current_user
from datetime import datetime, timezone

blogs_bp = Blueprint("blogs", __name__)

@blogs_bp.route("/blogs", methods=["POST"])
def create_blog():
    user, error, code = get_current_user()

    if error:
        return error, code

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not title or not content:
        return jsonify({"error": "title and content are required"}), 400

    blog = {
        "title": title,
        "content": content,
        "author_id": str(user["_id"]),
        "status": "draft",
        "created_at": datetime.now(timezone.utc)
    }

    result = mongo.db.blogs.insert_one(blog)

    return jsonify({
        "message": "Blog created as draft",
        "blog_id": str(result.inserted_id)
    }), 201
