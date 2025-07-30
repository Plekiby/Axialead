"""Initial migration for Course-Service

Revision ID: 0001_initial
Revises: 
Create Date: 2025-07-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# Identifiants de la migration
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Table categories
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
    )
    # Table courses
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('duration_hours', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    # Table d’association course_category
    op.create_table(
        'course_category',
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), primary_key=True),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('categories.id'), primary_key=True),
    )
    # Table course_documents
    op.create_table(
        'course_documents',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('url', sa.String(512), nullable=False),
    )
    # Table sessions
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('start_datetime', sa.DateTime, nullable=False),
        sa.Column('end_datetime', sa.DateTime, nullable=False),
        sa.Column('slots_total', sa.Integer, nullable=False),
        sa.Column('slots_remaining', sa.Integer, nullable=False),
    )
    # Table registrations
    op.create_table(
        'registrations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('session_id', sa.Integer, sa.ForeignKey('sessions.id'), nullable=False),
        sa.Column('user_id', sa.Integer, nullable=False),
    )

def downgrade():
    for tbl in ["registrations","sessions","course_documents","course_category","courses","categories"]:
        op.drop_table(tbl)
