from src.helpers.logging_helper import SystemLogging
from src.services import (
    user_service,
    moderator_service,
    timeout_service,
    custom_command_service,
    message_service,
)

syslog = SystemLogging(__name__)


def send_help_message(chat_id: int, reply_user: int, message_id: int):
    user = user_service.get_user(reply_user)

    custom_messages = ""

    for cc in custom_command_service.custom_commands:
        if cc["chat_id"] == chat_id:
            description = "Nenhuma descrição encontrada."

            if cc["description"] != None and len(cc["description"]) > 0:
                description = cc["description"]

            custom_messages += f"*!{cc['command']}:* {description}\n"

    cc_title = ""
    if len(custom_messages) > 0:
        cc_title = "\n*Comandos Customizados:*\n\n"

    help_message = (
        f"Olá, *{(user['username'])}*!\n"
        "Aqui está a minha lista de comandos disponiveis:\n\n"
        "*!help:* lista de comandos disponíveis\n"
        "*!mod username:* adiciona o usuário na lista de moderadores ×\n"
        "*!unmod username:* remove o usuário da lista de moderadores ×\n"
        "*!mute username tempo_em_segundos:* adiciona o usuário na lista de silenciados pelo tempo especificado ××\n"
        "*!unmute username:* remove o usuário da lista de silenciados ××\n"
        "*!add <comando> | <resposta> | <descrição>:* adiciona um novo comando (para mídias, enviar o comando na legenda) ××\n"
        f"{cc_title}"
        f"{custom_messages}"
        "\n× _necessário ser um administrador_\n"
        "×× _necessário ser um administrador ou moderador_"
    )

    message_service.send_message(chat_id, help_message)


def resolve_action(message):
    try:
        from_user_id = message["from"]["id"]
        chat_id = message["chat"]["id"]

        if timeout_service.is_user_in_timeout(chat_id, from_user_id):
            return

        # persistindo usuarios:
        user_service.add_user_if_not_exists(from_user_id, message["from"]["username"])

        text = ""

        if "text" in message:
            text = message["text"]
        elif "caption" in message:
            text = message["caption"]
        else:
            return

        if text.lower().startswith("!help"):
            send_help_message(chat_id, from_user_id, message["message_id"])
        elif text.lower().startswith("!mod"):
            moderator_service.insert_moderator(chat_id, text, from_user_id)
        elif text.lower().startswith("!unmod"):
            moderator_service.remove_moderator(chat_id, text, from_user_id)
        elif text.lower().startswith("!mute"):
            timeout_service.insert_timeout_user(chat_id, text, from_user_id)
        elif text.lower().startswith("!unmute"):
            timeout_service.remove_timeout_user(chat_id, text, from_user_id)
        elif text.lower().startswith("!add"):
            file_id = None
            media_type = None

            if "audio" in message:
                file_id = message["audio"]["file_id"]
                media_type = "audio"
            elif "photo" in message:
                file_id = message["photo"][2]["file_id"]
                media_type = "image"

            custom_command_service.insert_command(
                chat_id, text, from_user_id, file_id, media_type
            )
        elif text.startswith("!") and len(text) >= 3:

            custom_command = text.split(" ", 0)[0]
            custom_command = custom_command.split("!")[1]

            db_command = custom_command_service.get_command(custom_command, chat_id)

            if db_command:
                if db_command["media_type"] == "audio":
                    user = user_service.get_user(from_user_id)
                    message_service.send_audio(
                        chat_id,
                        db_command["file_id"],
                        db_command["text"],
                        user["username"],
                    )
                elif db_command["media_type"] == "image":
                    message_service.send_image(
                        chat_id, db_command["file_id"], db_command["text"]
                    )
                else:
                    message_service.send_message(chat_id, db_command["text"])

    except Exception as ex:
        syslog.create_warning("resolve_action", ex)
