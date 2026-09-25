
from flask import Blueprint, request, jsonify
from database import mongo
from middleware import get_current_user
from datetime import datetime

create_blog_bp = Blueprint("create_blog", __name__)

@create_blog_bp.route("/blogs", methods=["POST"])
def create_blog():
    user, error, code = get_current_user()
    if error:
        return error, code

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    tags = data.get("tags", [])

    if not title or not content:
        return jsonify({"error": "title and content are required"}), 400

    if not isinstance(tags, list):
        return jsonify({"error": "tags must be a list"}), 400

    now = datetime.utcnow()

    blog = {
        "title": title,
        "content": content,
        "author_id": str(user["_id"]),
        "status": "draft",
        "created_at": now,
        "updated_at": now,
        "published_at": None,
        "tags": tags,
        "likes": 0,
        "liked_by": []
    }

    result = mongo.db.blogs.insert_one(blog)

    return jsonify({
        "message": "Blog created as draft",
        "blog_id": str(result.inserted_id)
    }), 201
