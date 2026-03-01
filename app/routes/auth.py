import json
import os
import uuid

from flask import Blueprint, request
from app.utils.response import success_response, error_response

auth_bp = Blueprint("auth", __name__)

DATA_FILE = os.path.join("data", "users.json")


def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)


@auth_bp.post("/signup")
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password:
        return error_response("Email and password required", 400)

    users = load_users()
    if email in users:
        return error_response("User already exists", 409)

    users[email] = {
        "id": str(uuid.uuid4()),
        "email": email,
        "password": password,  # In real world, hash this!
        "name": name or email.split("@")[0],
    }
    save_users(users)

    return success_response({"message": "User created successfully"}, 201)


@auth_bp.post("/login")
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    users = load_users()
    user = users.get(email)
    if not user or user["password"] != password:
        return error_response("Invalid credentials", 401)

    # Return a mock token and user info
    return success_response(
        {"token": f"mock-jwt-token-{user['id']}", "user": {"id": user["id"], "email": user["email"], "name": user["name"]}},
        200
    )
