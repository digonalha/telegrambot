from src.repositories.database.config import base, session_local, engine

# necessário importar os modelos para que quando o método create_tables() for chamado,
# os modelos já estejam mapeados no metadata do declarative_base
from src.repositories.models import (
    user_model,
    moderator_model,
    custom_command_model,
    tracked_sale_model,
    sale_tracker_keyword_model,
)


def create_tables():
    base.metadata.create_all(bind=engine)


def get():
    db = session_local()

    try:
        return db
    finally:
        db.close()
