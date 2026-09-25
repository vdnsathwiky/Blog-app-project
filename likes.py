from flask import Blueprint, jsonify
from database import mongo
from middleware import get_current_user
from bson.objectid import ObjectId

likes_bp = Blueprint("likes", __name__)

@likes_bp.route("/blogs/<blog_id>/like", methods=["POST"])
def like_blog(blog_id):
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
        return jsonify({"error": "Only published blogs can be liked"}), 400

    user_id = str(user["_id"])

    if user_id in blog.get("liked_by", []):
        return jsonify({"error": "You already liked this blog"}), 400

    mongo.db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$inc": {"likes": 1}, "$push": {"liked_by": user_id}}
    )

    return jsonify({"message": "Blog liked successfully"}), 200

@likes_bp.route("/blogs/<blog_id>/like", methods=["DELETE"])
def unlike_blog(blog_id):
    user, error, code = get_current_user()
    if error:
        return error, code

    try:
        blog = mongo.db.blogs.find_one({"_id": ObjectId(blog_id)})
    except Exception:
        return jsonify({"error": "Invalid blog ID"}), 400

    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    user_id = str(user["_id"])

    if user_id not in blog.get("liked_by", []):
        return jsonify({"error": "You have not liked this blog"}), 400

    mongo.db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$inc": {"likes": -1}, "$pull": {"liked_by": user_id}}
    )

    return jsonify({"message": "Blog unliked successfully"}), 200
