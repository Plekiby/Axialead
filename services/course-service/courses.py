# services/course-service/courses.py

from flask import Blueprint, request, current_app, jsonify
from models import Course, Category
from schemas import CourseSchema, CategorySchema
from sqlalchemy.orm import joinedload

courses_bp = Blueprint('courses', __name__)
course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)


@courses_bp.route('/categories', methods=['POST'])
def create_category():
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
    data = course_schema.load(request.json)
    db = current_app.db
    cat_objs = db.query(Category).filter(
        Category.id.in_(data.pop('category_ids', []))
    ).all()
    course = Course(**data)
    course.categories = cat_objs
    db.add(course)
    db.commit()
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
