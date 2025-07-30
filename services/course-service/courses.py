# services/course-service/courses.py

from flask import Blueprint, request, current_app, jsonify
from models import Course, Category, CourseDocument
from schemas import CourseSchema, CategorySchema
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
import os

courses_bp = Blueprint('courses', __name__)
course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)


@courses_bp.route('/categories', methods=['POST'])
def create_category():
    # Affiche le JSON brut reçu pour debug
    print("RAW JSON:", request.get_data())

    # Puis continue la validation et la création
    data = category_schema.load(request.json)
    db = current_app.db
    cat = Category(**data)
    db.add(cat)
    db.commit()
    return jsonify(category_schema.dump(cat)), 201

@courses_bp.route('/categories', methods=['GET'])
def list_categories():
    cats = current_app.db.query(Category).all()
    return jsonify(categories_schema.dump(cats)), 200


@courses_bp.route('/', methods=['POST'])
def create_course():
    raw = request.json or {}
    # 1) récupérer les IDs de catégories depuis le JSON brut
    category_ids = raw.get('category_ids', [])

    # 2) charger directement une instance Course
    course = course_schema.load(raw)

    # 3) associer les catégories existantes
    db = current_app.db
    course.categories = db.query(Category).filter(
        Category.id.in_(category_ids)
    ).all()

    # 4) persister en base
    db.add(course)
    db.commit()

    # 5) retourner le JSON du cours
    return jsonify(course_schema.dump(course)), 201

@courses_bp.route('/', methods=['GET'])
def list_courses():
    courses = current_app.db.query(Course).options(
        joinedload(Course.categories)
    ).all()
    return jsonify(courses_schema.dump(courses)), 200


@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = current_app.db.query(Course).options(
        joinedload(Course.categories),
        joinedload(Course.documents)
    ).get(course_id)
    if not course:
        return jsonify({'error': 'Cours non trouvé'}), 404
    return jsonify(course_schema.dump(course)), 200


@courses_bp.route('/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    data = course_schema.load(request.json, partial=True)
    db = current_app.db
    course = db.query(Course).get(course_id)
    if not course:
        return jsonify({'error': 'Cours non trouvé'}), 404
    for key, val in data.items():
        setattr(course, key, val)
    db.commit()
    return jsonify(course_schema.dump(course)), 200


@courses_bp.route('/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    db = current_app.db
    course = db.query(Course).get(course_id)
    if not course:
        return jsonify({'error': 'Cours non trouvé'}), 404
    db.delete(course)
    db.commit()
    return '', 204

@courses_bp.route('/<int:course_id>/documents', methods=['POST'])
def upload_document(course_id):
    if 'file' not in request.files:
        return jsonify({"error":"Pas de fichier envoyé"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error":"Nom de fichier vide"}), 400

    filename = secure_filename(file.filename)
    # crée dossier s’il n’existe pas
    course_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(course_id))
    os.makedirs(course_folder, exist_ok=True)
    path = os.path.join(course_folder, filename)
    file.save(path)

    # crée l’enregistrement en base
    url = f"/uploads/{course_id}/{filename}"  # ou l’URL publique configurée
    doc = CourseDocument(course_id=course_id, name=filename, url=url)
    db = current_app.db
    db.add(doc)
    db.commit()

    from schemas import CourseDocumentSchema
    schema = CourseDocumentSchema()
    return jsonify(schema.dump(doc)), 201


@courses_bp.route('/<int:course_id>/documents', methods=['GET'])
def list_documents(course_id):
    db = current_app.db
    docs = db.query(CourseDocument).filter_by(course_id=course_id).all()
    from schemas import CourseDocumentSchema
    schema = CourseDocumentSchema(many=True)
    return jsonify(schema.dump(docs)), 200