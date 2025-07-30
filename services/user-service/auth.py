# services/user-service/auth.py

from flask import Blueprint, request, current_app, jsonify
from passlib.hash import bcrypt
import jwt
import datetime
from models import User
from schemas import RegisterSchema, LoginSchema, UserSchema

auth_bp = Blueprint('auth', __name__)
register_schema = RegisterSchema()
login_schema = LoginSchema()
user_schema = UserSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = register_schema.load(request.json)
    db = current_app.db
    if db.query(User).filter_by(email=data['email']).first():
        return jsonify({"error": "Email déjà utilisé"}), 400

    pw_hash = bcrypt.hash(data['password'])
    user = User(email=data['email'], password_hash=pw_hash)
    db.add(user)
    db.commit()

    token = jwt.encode({
        "sub": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")
    return jsonify({"token": token}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = login_schema.load(request.json)
    db = current_app.db
    user = db.query(User).filter_by(email=data['email']).first()
    if not user or not bcrypt.verify(data['password'], user.password_hash):
        return jsonify({"error": "Identifiants invalides"}), 401

    token = jwt.encode({
        "sub": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")
    return jsonify({"token": token}), 200
