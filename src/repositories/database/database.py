from repositories.database.config import base, session_local, engine

# necessário importar os modelos para que quando o método create_tables() for chamado,
# os modelos já estejam mapeados no metadata do declarative_base
from repositories.models import (
    user_model,
    moderator_model,
    command_model,
    sale_model,
    keyword_model,
    tracking_event_model,
    tracking_code_model,
)


def create_tables():
    base.metadata.create_all(bind=engine)


def get():
    db = session_local()

    try:
        return db
    finally:
        db.close()
