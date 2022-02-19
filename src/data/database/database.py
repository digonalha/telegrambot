from data.database.config import base, session_local, engine

# necessário importar os modelos para que quando o método create_tables() for chamado,
# os modelos já estejam mapeados no metadata do declarative_base
from domain.models import (
    command,
    keyword,
    moderator,
    sale,
    tracking_code,
    tracking_event,
    user,
)


def create_tables():
    base.metadata.create_all(bind=engine)


def get():
    db = session_local()

    try:
        return db
    finally:
        db.close()
