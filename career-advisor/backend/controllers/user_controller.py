from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os
import logging

from models import db, User

# Blueprint
user_bp = Blueprint('user_controller', __name__, url_prefix='/api/users')

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secret key from environment
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")


# ---------------------------
# Standard API Response
# ---------------------------
def api_response(success=True, message="", data=None, error=None, status=200):
    return jsonify({
        "success": success,
        "message": message,
        "data": data,
        "error": error
    }), status


# ---------------------------
# Token Middleware
# ---------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        auth_header = request.headers.get("Authorization")

        if auth_header:
            parts = auth_header.split(" ")
            if len(parts) == 2:
                token = parts[1]

        if not token:
            return api_response(False, "Token missing", status=401)

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['id'])

            if not current_user:
                return api_response(False, "User not found", status=404)

        except jwt.ExpiredSignatureError:
            return api_response(False, "Token expired", status=401)

        except jwt.InvalidTokenError:
            return api_response(False, "Invalid token", status=401)

        except Exception as e:
            logger.error(f"Token error: {str(e)}")
            return api_response(False, "Token error", error=str(e), status=500)

        return f(current_user, *args, **kwargs)

    return decorated


# ---------------------------
# Register
# ---------------------------
@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        # Validation
        if not email or "@" not in email:
            return api_response(False, "Invalid email", status=400)

        if not password or len(password) < 6:
            return api_response(False, "Password must be at least 6 characters", status=400)

        # Check duplicate
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return api_response(False, "Email already exists", status=409)

        # Create user
        hashed_pw = generate_password_hash(password)
        new_user = User(email=email, password=hashed_pw, name=name)

        db.session.add(new_user)
        db.session.commit()

        logger.info(f"User registered: {email}")

        return api_response(True, "User registered successfully", {
            "user_id": new_user.id,
            "email": new_user.email
        }, status=201)

    except Exception as e:
        logger.error(f"Register error: {str(e)}")
        return api_response(False, "Registration failed", error=str(e), status=500)


# ---------------------------
# Login
# ---------------------------
@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return api_response(False, "Invalid credentials", status=401)

        token = jwt.encode({
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")

        return api_response(True, "Login successful", {
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        })

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return api_response(False, "Login failed", error=str(e), status=500)


# ---------------------------
# Logout
# ---------------------------
@user_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    return api_response(True, "Logged out successfully")


# ---------------------------
# Get Profile
# ---------------------------
@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return api_response(True, "Profile fetched", {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    })


# ---------------------------
# Update Profile
# ---------------------------
@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json()

        if 'name' in data:
            current_user.name = data['name']

        if 'password' in data:
            if len(data['password']) < 6:
                return api_response(False, "Password too short", status=400)
            current_user.password = generate_password_hash(data['password'])

        db.session.commit()

        return api_response(True, "Profile updated")

    except Exception as e:
        logger.error(f"Update error: {str(e)}")
        return api_response(False, "Update failed", error=str(e), status=500)


# ---------------------------
# Reset Password (Mock)
# ---------------------------
@user_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        email = data.get('email')

        user = User.query.filter_by(email=email).first()

        if not user:
            return api_response(False, "User not found", status=404)

        return api_response(True, "Password reset link sent")

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# Check Token (Mobile Support)
# ---------------------------
@user_bp.route('/check-token', methods=['GET'])
@token_required
def check_token(current_user):
    return api_response(True, "Token valid", {
        "user_id": current_user.id
    })


# ---------------------------
# Delete Account
# ---------------------------
@user_bp.route('/delete', methods=['DELETE'])
@token_required
def delete_account(current_user):
    try:
        db.session.delete(current_user)
        db.session.commit()

        return api_response(True, "Account deleted")

    except Exception as e:
        return api_response(False, "Delete failed", error=str(e), status=500)


# ---------------------------
# Admin: List Users
# ---------------------------
@user_bp.route('/all', methods=['GET'])
def list_users():
    try:
        users = User.query.all()

        return api_response(True, "Users fetched", [
            {"id": u.id, "email": u.email, "name": u.name}
            for u in users
        ])

    except Exception as e:
        return api_response(False, "Error fetching users", error=str(e), status=500)