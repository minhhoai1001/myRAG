# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
import os

# Load environment variables from .env file (look in parent directory)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# ---- Đọc config Alembic
config = context.config

# Logging
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except KeyError:
        # Logging configuration not found in alembic.ini, use default logging
        pass

# ---- Import Base metadata từ app
# Cho phép lấy DATABASE_URL từ env (ưu tiên) thay vì alembic.ini
# Import DATABASE_URL from app.db as fallback (which has a default)
from app.db import DATABASE_URL, Base  # noqa
import app.models  # noqa: F401  # ensure models are imported to populate Base.metadata

# Use environment variable if set, otherwise use the default from app.db
database_url = os.getenv("DATABASE_URL", DATABASE_URL)
if not database_url or database_url.strip() == "":
    raise ValueError(
        "DATABASE_URL is not set. Please set it as an environment variable "
        "or ensure app.db has a valid default DATABASE_URL."
    )
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,    # so sánh type khi autogenerate
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=False,  # True nếu migrate SQLite
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
