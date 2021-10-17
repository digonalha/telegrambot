import os
from dotenv import load_dotenv
from src.repositories.models.custom_command_model import MediaType
from src.helpers.logging_helper import SystemLogging
from src.services import (
    user_service,
    moderator_service,
    timeout_service,
    custom_command_service,
    message_service,
    keyword_service,
)

load_dotenv()

BOT_NAME = os.getenv("BOT_NAME")
MAX_COMMANDS = os.getenv("TOTAL_COMMANDS")

syslog = SystemLogging(__name__)


def send_custom_commands_message(chat_id: int, name: str, message_id: int):
    """Send a list of custom commands when asked on chat."""
    custom_messages = ""

    custom_command_service.custom_commands.sort(key=lambda x: x.command)

    total_commands = 0

    for cc in custom_command_service.custom_commands:
        if cc.chat_id == chat_id:
            total_commands += 1
            description = "Nenhuma descrição encontrada"

            if cc.description and len(cc.description) > 0:
                description = cc.description

            custom_messages += f"*/{cc.command}:* {description}\n"

    if len(custom_messages) == 0:
        message_service.send_message(
            chat_id,
            "Nenhum comando customizado encontrado para o grupo. Utilize o comando /addcmd para cadastrar novos comandos",
        )
        return

    max_cmd = MAX_COMMANDS if MAX_COMMANDS else 10

    help_message = (
        f"Olá, *{(name)}*!\n"
        "Aqui estão os comandos customizados disponíveis no grupo:\n\n"
        f"{custom_messages}"
        f"\n*Total: {str(total_commands)}/{str(max_cmd)}*"
    )

    message_service.send_message(chat_id, help_message)


def send_group_help_message(chat_id: int, name: str, message_id: int) -> None:
    """Send help message when asked on chat."""

    help_message = (
        f"Olá, *{(name)}*!\n"
        "Aqui estão os meus comandos disponíveis:\n\n"
        "*/help:* lista os comandos disponíveis\n"
        "*/mod <username>:* promove o usuário ao cargo de moderador \*\n"
        "*/unmod <username>:* rebaixa o usuário do cargo de moderador \*\n"
        "*/mute <username> <tempo em segundos>:* adiciona o usuário na lista de silenciados pelo tempo especificado \*\*\n"
        "*/unmute <username>:* remove o usuário da lista de silenciados \*\*\n"
        "*/cmd:* lista os comandos customizados disponíveis no grupo\n"
        "*/addcmd <comando> | <resposta> | <descrição>:* adiciona um novo comando (para mídias, enviar o comando na legenda) \*\*\n"
        "*/delcmd <comando>:* remove um comando customizado \*\n"
        "\n\* _necessário ser um administrador_\n"
        "\*\* _necessário ser um administrador ou moderador_\n"
    )

    if BOT_NAME:
        help_message += (
            f"\nPara monitorar promoções, enviar /help no privado para @{BOT_NAME}"
        )
    else:
        help_message += "\nPara monitorar promoções, enviar /help no privado"

    message_service.send_message(chat_id, help_message)


def send_private_help_message(chat_id: int, name: str, message_id: int) -> None:
    help_message = (
        f"Olá, *{(name)}*!\n"
        "Aqui estão os meus comandos disponíveis:\n\n"
        "*/help:* lista os comandos disponíveis\n"
        "*/promo:* lista as promoções cadastradas pelo usuário"
        "*/addpromo <palavra-chave>:* monitora e notifica promoções referentes a palavra-chave\n"
        "*/delpromo <palavra-chave>:* remove a palavra-chave da lista de monitoramento de promoções\n"
        "*/clearpromo:* remove todas as palavras-chave da lista de monitoramento de promoções\n"
    )

    message_service.send_message(chat_id, help_message)


def resolve_action(message) -> None:
    """Select an action to answer a message update."""
    try:
        from_user_id = message["from"]["id"]
        chat_id = message["chat"]["id"]

        if timeout_service.is_user_in_timeout(chat_id, from_user_id):
            return

        username = ""

        if "username" in message["from"]:
            username = message["from"]["username"]
        # if user who send message not found on users object, add on database:
        user_service.add_or_update_user(
            from_user_id, message["from"]["first_name"], username
        )

        text = ""

        if "text" in message:
            text = message["text"]
        elif "caption" in message:
            text = message["caption"]
        else:
            return

        if not text.startswith("/"):
            return

        is_group = message["chat"]["type"] == "group"

        if is_group:
            if text.lower() == "/help" or (
                BOT_NAME and text.lower() == f"/help@{BOT_NAME}"
            ):
                send_group_help_message(
                    chat_id, message["from"]["first_name"], message["message_id"]
                )
                return
            elif text.lower() == "/cmd" or (
                BOT_NAME and text.lower() == f"/cmd@{BOT_NAME}"
            ):
                send_custom_commands_message(
                    chat_id, message["from"]["first_name"], message["message_id"]
                )
                return
            elif text.lower().startswith("/mod"):
                moderator_service.insert_moderator(chat_id, text, from_user_id)
                return
            elif text.lower().startswith("/unmod"):
                moderator_service.remove_moderator(chat_id, text, from_user_id)
                return
            elif text.lower().startswith("/mute"):
                timeout_service.insert_timeout_user(chat_id, text, from_user_id)
                return
            elif text.lower().startswith("/unmute"):
                timeout_service.remove_timeout_user(chat_id, text, from_user_id)
                return
            elif text.lower().startswith("/addcmd"):
                file_id = None
                media_type = MediaType.NONE

                if "audio" in message:
                    file_id = message["audio"]["file_id"]
                    media_type = MediaType.AUDIO
                elif "photo" in message:
                    file_id = message["photo"][2]["file_id"]
                    media_type = MediaType.IMAGE
                elif "animation" in message:
                    file_id = message["animation"]["file_id"]
                    media_type = MediaType.ANIMATION

                custom_command_service.insert_command(
                    chat_id, text, from_user_id, file_id, media_type
                )

                return
            elif text.lower().startswith("/delcmd"):
                custom_command_service.remove_command(chat_id, text, from_user_id)
                return
            elif len(text) >= 3:
                custom_command = text.split(" ", 0)[0].split("/")[1].lower()
                db_command = custom_command_service.get_command(custom_command, chat_id)

                if db_command:
                    if db_command.media_type == MediaType.AUDIO:
                        user = user_service.get_user_by_id_if_exists(from_user_id)
                        message_service.send_audio(
                            chat_id,
                            db_command.file_id,
                            db_command.text,
                            user.user_name,
                        )
                    elif db_command.media_type == MediaType.IMAGE:
                        message_service.send_image(
                            chat_id, db_command.file_id, db_command.text
                        )
                    elif db_command.media_type == MediaType.ANIMATION:
                        message_service.send_animation(chat_id, db_command.file_id)
                    else:
                        message_service.send_message(chat_id, db_command.text)
                return
        else:
            if text.lower() == "/help" or text.lower() == "/start":
                send_private_help_message(
                    chat_id, message["from"]["first_name"], message["message_id"]
                )
            elif text.lower() == "/promo":
                keyword_service.get_user_keywords(
                    chat_id, from_user_id, message["message_id"]
                )
            elif text.lower() == "/clearpromo":
                keyword_service.remove_all_keywords(
                    chat_id, from_user_id, message["message_id"]
                )
            elif text.lower().startswith("/addpromo"):
                keyword_service.insert_keyword(
                    chat_id, text, from_user_id, message["message_id"]
                )
            elif text.lower().startswith("/delpromo"):
                keyword_service.remove_keyword(
                    chat_id, text, from_user_id, message["message_id"]
                )

    except Exception as ex:
        syslog.create_warning("resolve_action", ex)
