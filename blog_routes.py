from flask import Blueprint, request, jsonify
from database import mongo
from middleware import get_current_user
from bson.objectid import ObjectId

blog_routes_bp = Blueprint("blog_routes", __name__)

def blog_response(blog):
    return {
        "id": str(blog["_id"]),
        "title": blog["title"],
        "content": blog["content"],
        "status": blog["status"],
        "created_at": blog["created_at"],
        "updated_at": blog["updated_at"],
        "published_at": blog.get("published_at"),
        "tags": blog.get("tags", []),
        "likes": blog.get("likes", 0)
    }

@blog_routes_bp.route("/blogs", methods=["GET"])
def get_blogs():
    search = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip()

    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        if page < 1 or limit < 1 or limit > 100:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid page or limit"}), 400

    query = {"status": "published"}

    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}}
        ]

    if tag:
        query["tags"] = tag

    total = mongo.db.blogs.count_documents(query)
    skip = (page - 1) * limit

    blogs = list(
        mongo.db.blogs.find(query)
        .sort("published_at", -1)
        .skip(skip)
        .limit(limit)
    )

    return jsonify({
        "blogs": [blog_response(blog) for blog in blogs],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }), 200

@blog_routes_bp.route("/blogs/<blog_id>", methods=["GET"])
def get_one_blog(blog_id):
    try:
        blog = mongo.db.blogs.find_one({"_id": ObjectId(blog_id)})
    except Exception:
        return jsonify({"error": "Invalid blog ID"}), 400

    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    if blog["status"] == "draft":
        user, error, code = get_current_user()
        if error:
            return error, code

        if blog["author_id"] != str(user["_id"]):
            return jsonify({"error": "You cannot view this draft"}), 403

    return jsonify(blog_response(blog)), 200
