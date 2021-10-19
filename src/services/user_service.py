from datetime import datetime
from src.repositories.models.user_model import User
from src.helpers.logging_helper import SystemLogging
from src.repositories import user_repository
from src.schemas import user_schema
from src.services import moderator_service, message_service

users = []
syslog = SystemLogging(__name__)


def validate_user_permission(
    chat_id: int, user_id: int, validate_admin_only: bool = False
) -> bool:
    """Validate if user is admin or moderator."""
    user_send = next((u for u in users if u.user_id == user_id), None)

    if not user_send and validate_admin_only == True:
        return False
    elif (not user_send or not user_send.is_admin) and not next(
        (
            m
            for m in moderator_service.moderators
            if m.chat_id == chat_id and m.user_id == user_id
        ),
        None,
    ):
        message_service.send_message(
            chat_id, "Você não tem permissão para utilizar esse comando"
        )
        return False

    return True


def get_user_by_username_if_exists(chat_id: int, username: int) -> User:
    """Get user by username if exists on global users variable."""
    if username.startswith("@"):
        username = username.split("@")[1]

    user = next((u for u in users if u.user_name == username), None)

    if user == None:
        message_service.send_message(
            chat_id,
            f"Eu ainda não conheço o usuário *{username}* :(",
        )
        return False

    return user


def get_user_by_id_if_exists(user_id: int) -> User:
    """Get user by user_id from  global variable users if exists."""
    return next(
        (u for u in users if u.user_id == user_id),
        None,
    )


def get_all_users() -> None:
    """Fill the global variable users with all users found in database."""
    global users
    users = user_repository.get_all()


def add_or_update_user(user_id: int, first_name: str, user_name: str) -> None:
    """Create a new user on database if not exists, or update if necessary."""
    try:
        if next(
            (
                u
                for u in users
                if u.user_id == user_id
                and u.first_name == first_name
                and u.user_name == user_name
            ),
            None,
        ):
            return

        db_user = user_repository.get_by_id(user_id)

        if not db_user:
            now = datetime.now()

            db_user = user_repository.add(
                user_schema.UserCreate(
                    user_id=user_id,
                    user_name=user_name,
                    first_name=first_name,
                    is_admin=False,
                    table_width=0,
                    created_on=now,
                    modified_on=now,
                )
            )

            if db_user:
                users.append(db_user)
        elif db_user.user_name != user_name or db_user.first_name != first_name:

            updated_user = user_repository.update(
                user_schema.UserUpdate(
                    user_id=user_id,
                    user_name=user_name,
                    first_name=first_name,
                    modified_on=datetime.now(),
                )
            )

            if updated_user:
                try:
                    users.remove(db_user)
                    users.append(updated_user)
                except:
                    get_all_users()

    except Exception as ex:
        syslog.create_warning("add_user_if_not_exists", ex)


def update_width(user_id: int, text: str):
    try:
        command, width = text.split()

        if command != "/promotbl":
            raise

        width = int(width)
    except:
        message_service.send_image(
            user_id,
            file_id="AgACAgEAAxkBAAIVmGFuOHNMmUI4pThhiPDYznKAuIfeAAJnqjEbqi5xR5sI3gSDZJJfAQADAgADeAADIQQ",
            message=f"Você pode alterar o layout da sua lista de palavras-chave (retornada pelo comando /promo)! Para isso, é necessário que você envie o comando /promotbl passando como parâmetro o seu tamanho de layout preferido.\n\nEx. /promotbl 20\n\n_O tamanho 0 é o padrão (layout  de tabela desativado)_\n_Tamanhos entre 10 e 30 são bons para smartphones (eu uso o tamanho 23!)_\n_Tamanhos acima de 30 só ficam legais de exibir em tablets/computadores_",
        )
        return

    if width != 0 and (width < 10 or width > 50):
        message_service.send_message(
            user_id,
            f"Largura da tabela inválida. Escolha um valor entre 10 e 50 colunas. Para desativar a exibição de tabela, utilize o valor 0 como parâmetro",
        )
        return

    db_user = user_repository.get_by_id(user_id)

    old_width = db_user.table_width

    updated_user = user_repository.update_width(
        user_schema.UserUpdateWidth(
            user_id=user_id,
            table_width=width,
            modified_on=datetime.now(),
        )
    )

    if updated_user:
        try:
            users.remove(db_user)
            users.append(updated_user)
        except:
            get_all_users()

        message_service.send_message(
            user_id,
            f"Exibição de tabela ativado, largura atualizada de {old_width} para {updated_user.table_width}"
            if updated_user.table_width > 0
            else "Modo de exibição de tabela desativado",
        )
    else:
        message_service.send_message(
            user_id,
            f"Não foi possível atualizar a largura da tabela",
        )
