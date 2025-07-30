# services/user-service/users.py

from flask import Blueprint, request, current_app, jsonify
from functools import wraps
import jwt
from models import User
from schemas import UserSchema

user_bp = Blueprint('users', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        prefix = 'Bearer '
        if not auth.startswith(prefix):
            return jsonify({"error": "Token manquant"}), 401
        token = auth[len(prefix):]
        try:
            payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            request.user_id = payload['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expiré"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token invalide"}), 401
        return f(*args, **kwargs)
    return decorated

@user_bp.route('/', methods=['GET'])
@login_required
def list_users():
    db = current_app.db
    users = db.query(User).all()
    return jsonify(users_schema.dump(users)), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    db = current_app.db
    user = db.query(User).get(user_id)
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    return jsonify(user_schema.dump(user)), 200

@user_bp.route('/', methods=['DELETE'])
@login_required
def delete_user():
    data = request.get_json() or {}
    user_id = data.get("id")
    if not user_id:
        return jsonify({"error": "ID requis"}), 400
    db = current_app.db
    user = db.query(User).get(user_id)
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    db.delete(user)
    db.commit()
    return jsonify({}), 204
