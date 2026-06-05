from flask import Blueprint, request, jsonify
from model import db, user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
auth_bp = Blueprint("auth", __name__)
#register
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400
    required_fields = ["name", "email", "password", "gender"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "success": False,
                "message": f"{field.capitalize()} is required"
            }), 400
    existing_user = user.query.filter_by(
        email=data.get("email")
    ).first()
    if existing_user:
        return jsonify({
            "success": False,
            "message": "Email already registered"
        }), 400
    new_user = user(
        name=data.get("name"),
        email=data.get("email"),
        password=generate_password_hash(data.get("password")),
        phone=data.get("phone"),
        gender=data.get("gender"),
        role="user",
        status="active"
     )

    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Registration successful"
    }), 201

#login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400
    if not data.get("email") or not data.get("password"):
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400
    current_user = user.query.filter_by(
        email=data.get("email")
    ).first()
    if not current_user:
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401
    if current_user.status == "blacklisted":
        return jsonify({
            "success": False,
            "message": "Account is blacklisted"
        }), 403
    if not check_password_hash(
        current_user.password,
        data.get("password")
    ):
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=str(current_user.userid),
        additional_claims={
            "role": current_user.role
        }
    )

    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": access_token,
        "userid": current_user.userid,
        "name": current_user.name,
        "role": current_user.role
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():

    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200