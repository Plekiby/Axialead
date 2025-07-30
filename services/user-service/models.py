# services/course-service/models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Table, func
)
from sqlalchemy.orm import relationship

Base = declarative_base()

# Table d’association Course <-> Category (many-to-many)
course_category = Table(
    'course_category', Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    duration_hours = Column(Integer, nullable=False)        # nombre d’heures pour valider
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    categories = relationship(
        'Category',
        secondary=course_category,
        back_populates='courses'
    )
    documents = relationship(
        'CourseDocument',
        back_populates='course',
        cascade='all, delete-orphan'
    )
    sessions = relationship(
        'Session',
        back_populates='course',
        cascade='all, delete-orphan'
    )

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    courses = relationship(
        'Course',
        secondary=course_category,
        back_populates='categories'
    )

class CourseDocument(Base):
    __tablename__ = 'course_documents'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(512), nullable=False)

    course = relationship('Course', back_populates='documents')

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    slots_total = Column(Integer, nullable=False)
    slots_remaining = Column(Integer, nullable=False)

    course = relationship('Course', back_populates='sessions')
    registrations = relationship(
        'Registration',
        back_populates='session',
        cascade='all, delete-orphan'
    )

class Registration(Base):
    __tablename__ = 'registrations'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    user_id = Column(Integer, nullable=False)  # on stocke uniquement l’ID du user-service

    session = relationship('Session', back_populates='registrations')
