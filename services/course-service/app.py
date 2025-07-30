# services/course-service/app.py

import os
from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Import pour gérer les erreurs de schéma et JSON mal formé
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest

# Import des blueprints
from courses import courses_bp
from sessions import sessions_bp

def create_app():
    app = Flask(__name__)

    # 1) Chemin physique où seront sauvés les fichiers uploadés
    upload_folder = os.path.join(os.getcwd(), 'services', 'course-service', 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    # 2) Permettre l’accès public aux fichiers via /uploads/…
    @app.route('/uploads/<int:course_id>/<path:filename>')
    def uploaded_file(course_id, filename):
        # Sert static/uploads/<course_id>/<filename>
        directory = os.path.join(app.config['UPLOAD_FOLDER'], str(course_id))
        return app.send_from_directory(directory, filename)

    # Configuration de la BDD (AlwaysData)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        "mysql+pymysql://axialead:Ght92vtt?@"
        "mysql-axialead.alwaysdata.net:3306/axialead_db"
    )

    # Chemin physique où on stocke les fichiers
    upload_folder = os.path.join(os.getcwd(), 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Initialisation de SQLAlchemy « à la main »
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], pool_pre_ping=True)
    SessionFactory = sessionmaker(bind=engine)
    app.db = scoped_session(SessionFactory)

    # Enregistrement des blueprints
    app.register_blueprint(courses_bp, url_prefix='/courses')
    app.register_blueprint(sessions_bp, url_prefix='/sessions')

    @app.route('/')
    def index():
        return jsonify({"msg": "Course-Service en ligne"}), 200

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        app.db.remove()

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        # err.messages est un dict { champ: ['msg1', ...] }
        return jsonify({"errors": err.messages}), 400

    @app.errorhandler(400)
    def handle_bad_request(err):
        return jsonify({"error": "Requête JSON invalide"}), 400

    return app

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=5001)
