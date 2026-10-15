from alembic import context
from app.persistence import Base, engine

config = context.config
with engine.connect() as connection:
    context.configure(
        connection=connection, target_metadata=Base.metadata, render_as_batch=engine.dialect.name == "sqlite"
    )
    with context.begin_transaction():
        context.run_migrations()
