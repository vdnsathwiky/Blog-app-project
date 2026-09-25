# Flask Blog Management API

Simple backend Blog API built using Flask and MongoDB.

## Tech Stack

- Python
- Flask
- MongoDB
- JWT

## Features

- User Registration & Login
- JWT Authentication
- Create Blog
- Edit Blog
- Publish Blog
- Delete Blog
- Get Blogs
- Search & Pagination
- Like / Unlike
- Comments

## Project Structure

    app.py
    auth.py
    config.py
    database.py
    middleware.py
    create_blog.py
    blog_routes.py
    blog_actions.py
    likes.py
    comments.py
    requirements.txt

## Setup

### Install Dependencies

    pip install -r requirements.txt

### Create .env File

    MONGO_URI=your_mongodb_connection_string
    JWT_SECRET=your_secret_key

### Run the Application

    python app.py

### Server

    http://127.0.0.1:5000

## Authentication

Protected APIs require:

    Authorization: Bearer YOUR_TOKEN
