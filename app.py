from flask import Flask, jsonify
from database import mongo
from config import MONGO_URI
from auth import auth_bp
from create_blog import create_blog_bp
from blog_routes import blog_routes_bp
from blog_actions import blog_actions_bp
from likes import likes_bp
from comments import comments_bp

app = Flask(__name__)

app.config["MONGO_URI"] = MONGO_URI

mongo.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(create_blog_bp, url_prefix="/api")
app.register_blueprint(blog_routes_bp, url_prefix="/api")
app.register_blueprint(blog_actions_bp, url_prefix="/api")
app.register_blueprint(likes_bp, url_prefix="/api")
app.register_blueprint(comments_bp, url_prefix="/api")


@app.route("/")
def home():
    return jsonify({"message": "Blog API is running"})


if __name__ == "__main__":
    app.run(debug=True)
