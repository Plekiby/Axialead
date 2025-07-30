# services/course-service/sessions.py

from flask import Blueprint, request, current_app, jsonify
from models import Session, Registration
from schemas import SessionSchema, RegistrationSchema

sessions_bp = Blueprint('sessions', __name__)
session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)
registration_schema = RegistrationSchema()


@sessions_bp.route('/', methods=['POST'])
def create_session():
    data = session_schema.load(request.json)
    db = current_app.db
    session = Session(**data)
    db.add(session)
    db.commit()
    return jsonify(session_schema.dump(session)), 201


@sessions_bp.route('/', methods=['GET'])
def list_sessions():
    sessions = current_app.db.query(Session).all()
    return jsonify(sessions_schema.dump(sessions)), 200


@sessions_bp.route('/<int:session_id>/register', methods=['POST'])
def register_user(session_id):
    db = current_app.db
    session = db.query(Session).get(session_id)
    if not session:
        return jsonify({'error': 'Session non trouvée'}), 404
    if session.slots_remaining < 1:
        return jsonify({'error': 'Plus de places disponibles'}), 400

    data = {'session_id': session_id, 'user_id': request.json.get('user_id')}
    reg = Registration(**data)
    session.slots_remaining -= 1
    db.add(reg)
    db.commit()
    return jsonify(registration_schema.dump(reg)), 201
