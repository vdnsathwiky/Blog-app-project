from flask import Blueprint, request, jsonify
from database import mongo
from middleware import get_current_user
from bson.objectid import ObjectId
from datetime import datetime , timezone

blog_actions_bp = Blueprint("blog_actions", __name__)

@blog_actions_bp.route("/blogs/<blog_id>", methods=["PUT"])
def edit_blog(blog_id):
    user, error, code = get_current_user()
    if error:
        return error, code

    try:
        blog = mongo.db.blogs.find_one({"_id": ObjectId(blog_id)})
    except Exception:
        return jsonify({"error": "Invalid blog ID"}), 400

    if not blog:
        return jsonify({"error": "Blog not found"}), 404
    if blog["author_id"] != str(user["_id"]):
        return jsonify({"error": "You can edit only your own blog"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    title = data.get("title", blog["title"]).strip()
    content = data.get("content", blog["content"]).strip()
    tags = data.get("tags", blog.get("tags", []))
    if not title or not content:
        return jsonify({"error": "title and content cannot be empty"}), 400

    if not isinstance(tags, list):
        return jsonify({"error": "tags must be a list"}), 400
    mongo.db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$set": {
            "title": title,
            "content": content,
            "tags": tags,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    return jsonify({"message": "Blog updated successfully"}), 200

@blog_actions_bp.route("/blogs/<blog_id>/publish", methods=["PATCH"])
def publish_blog(blog_id):
    user, error, code = get_current_user()
    if error:
        return error, code

    try:
        blog = mongo.db.blogs.find_one({"_id": ObjectId(blog_id)})
    except Exception:
        return jsonify({"error": "Invalid blog ID"}), 400
    if not blog:
        return jsonify({"error": "Blog not found"}), 404
    if blog["author_id"] != str(user["_id"]):
        return jsonify({"error": "You can publish only your own blog"}), 403
    if blog["status"] == "published":
        return jsonify({"error": "Blog is already published"}), 400

    now = datetime.now(timezone.utc)
    mongo.db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$set": {
            "status": "published",
            "published_at": now,
            "updated_at": now
        }}
    )
    return jsonify({"message": "Blog published successfully"}), 200

@blog_actions_bp.route("/blogs/<blog_id>", methods=["DELETE"])
def delete_blog(blog_id):
    user, error, code = get_current_user()
    if error:
        return error, code
    try:
        blog = mongo.db.blogs.find_one({"_id": ObjectId(blog_id)})
    except Exception:
        return jsonify({"error": "Invalid blog ID"}), 400
    if not blog:
        return jsonify({"error": "Blog not found"}), 404
    if blog["author_id"] != str(user["_id"]) and user.get("role") != "admin":
        return jsonify({"error": "You can delete only your own blog"}), 403
    mongo.db.blogs.delete_one({"_id": ObjectId(blog_id)})
    return jsonify({"message": "Blog deleted successfully"}), 200

@blog_actions_bp.route("/me/blogs", methods=["GET"])
def my_blogs():
    user, error, code = get_current_user()
    if error:
        return error, code
    status = request.args.get("status", "").strip()
    if status and status not in ["draft", "published"]:
        return jsonify({"error": "status must be draft or published"}), 400
    query = {"author_id": str(user["_id"])}
    if status:
        query["status"] = status
    blogs = list(mongo.db.blogs.find(query).sort("created_at", -1))
    result = []
    for blog in blogs:
        result.append({
            "id": str(blog["_id"]),
            "title": blog["title"],
            "content": blog["content"],
            "status": blog["status"],
            "tags": blog.get("tags", []),
            "likes": blog.get("likes", 0)
        })
    return jsonify({"blogs": result}), 200
