# services/course-service/migrations/env.py

import os, sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import importlib.util

# 1) Détermine le chemin vers services/course-service
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# 2) Charge dynamiquement models.py
models_path = os.path.join(parent_dir, "models.py")
spec = importlib.util.spec_from_file_location("models", models_path)
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)
Base = models.Base

# Alembic Config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData pour autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata,
        literal_binds=True, dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
