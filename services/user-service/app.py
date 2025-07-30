# services/user-service/app.py

from flask import Flask, jsonify
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from auth import auth_bp
from users import user_bp

def create_app():
    app = Flask(__name__)
    app.config.update({
        "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://axialead:Ght92vtt?@mysql-axialead.alwaysdata.net:3306/axialead_db",
        "JWT_SECRET_KEY": "CHANGE_ME_AVEC_UN_SECRET_COMPLEXE",
    })

    # Base SQLAlchemy
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], pool_pre_ping=True)
    Base.metadata.bind = engine
    session_factory = sessionmaker(bind=engine)
    app.db = scoped_session(session_factory)

    # Enregistrer blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")

    @app.teardown_appcontext
    def remove_session(exception=None):
        app.db.remove()

    @app.route("/")
    def index():
        return jsonify({"msg": "User-Service en ligne"}), 200

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)
