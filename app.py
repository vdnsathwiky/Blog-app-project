from flask import Flask, jsonify
from database import mongo
from config import MONGO_URI
from auth import auth_bp
from blogs import blogs_bp

app = Flask(__name__)

app.config["MONGO_URI"] = MONGO_URI

mongo.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(blogs_bp, url_prefix="/api")


@app.route("/")
def home():
    return jsonify({"message": "Blog API is running"})


if __name__ == "__main__":
    app.run(debug=True)