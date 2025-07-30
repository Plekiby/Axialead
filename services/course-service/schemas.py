# services/course-service/schemas.py
from marshmallow import Schema, fields, validate, post_load
from models import Course, Category, CourseDocument, Session, Registration

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )

class CourseDocumentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(max=255))
    url = fields.Url(required=True, validate=validate.Length(max=512))

class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(max=255))
    description = fields.Str()
    price = fields.Float(required=True)
    duration_hours = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)

    # Associations
    categories = fields.Nested(CategorySchema, many=True, dump_only=True)
    category_ids = fields.List(fields.Int(), load_only=True)
    documents = fields.Nested(CourseDocumentSchema, many=True, dump_only=True)

    @post_load
    def make_course(self, data, **kwargs):
        data.pop('category_ids', None)
        return Course(**data)
        
class SessionSchema(Schema):
    id = fields.Int(dump_only=True)
    course_id = fields.Int(required=True)
    start_datetime = fields.DateTime(required=True)
    end_datetime = fields.DateTime(required=True)
    slots_total = fields.Int(required=True)
    slots_remaining = fields.Int(dump_only=True)

    @post_load
    def make_session(self, data, **kwargs):
        return Session(**data)


class RegistrationSchema(Schema):
    id = fields.Int(dump_only=True)
    session_id = fields.Int(required=True)
    user_id = fields.Int(required=True)

    @post_load
    def make_registration(self, data, **kwargs):
        return Registration(**data)
