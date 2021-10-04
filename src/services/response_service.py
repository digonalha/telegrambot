from src.repositories.models.custom_command_model import MediaType
from src.helpers.logging_helper import SystemLogging
from src.services import (
    user_service,
    moderator_service,
    timeout_service,
    custom_command_service,
    message_service,
    sale_tracker_keyword_service,
)

syslog = SystemLogging(__name__)


def send_help_message(chat_id: int, reply_user: int, message_id: int) -> None:
    """Send help message when asked on chat."""
    user = user_service.get_user_by_id_if_exists(reply_user)

    custom_messages = ""

    custom_command_service.custom_commands.sort(key=lambda x: x.command)

    for cc in custom_command_service.custom_commands:
        if cc.chat_id == chat_id:
            description = "Nenhuma descrição encontrada"

            if cc.description and len(cc.description) > 0:
                description = cc.description

            custom_messages += f"*!{cc.command}:* {description}\n"

    cc_title = ""
    if len(custom_messages) > 0:
        cc_title = "\n*Comandos Customizados:*\n\n"

    help_message = (
        f"Olá, *@{(user.user_name)}*!\n"
        "Aqui está a minha lista de comandos disponíveis:\n\n"
        "*!help:* lista de comandos disponíveis\n"
        "*!mod username:* adiciona o usuário na lista de moderadores \*\n"
        "*!unmod username:* remove o usuário da lista de moderadores \*\n"
        "*!mute username tempo em segundos:* adiciona o usuário na lista de silenciados pelo tempo especificado \*\*\n"
        "*!unmute username:* remove o usuário da lista de silenciados \*\*\n"
        "*!track palavra-chave:* monitora e notifica promoções referentes a palavra-chave \*\*\n"
        "*!untrack palavra-chave:* remove a palavra-chve da lista de monitoramento \*\*\n"
        "*!add comando | resposta | descrição:* adiciona um novo comando (para mídias, enviar o comando na legenda) \*\*\n"
        "*!del comando:* remove um comando customizado\*\n"
        f"{cc_title}"
        f"{custom_messages}"
        "\n\* _necessário ser um administrador_\n"
        "\*\* _necessário ser um administrador ou moderador_"
    )

    message_service.send_message(chat_id, help_message)


def resolve_action(message) -> None:
    """Select an action to answer a message update."""
    try:
        from_user_id = message["from"]["id"]
        chat_id = message["chat"]["id"]

        if timeout_service.is_user_in_timeout(chat_id, from_user_id):
            return

        # if user who send message not found on users object, add on database:
        user_service.add_user_if_not_exists(from_user_id, message["from"]["username"])

        text = ""

        if "text" in message:
            text = message["text"]
        elif "caption" in message:
            text = message["caption"]
        else:
            return

        if not text.startswith("!"):
            return

        is_group = message["chat"]["type"] == "group"

        if is_group:
            if text.lower().startswith("!help"):
                send_help_message(chat_id, from_user_id, message["message_id"])
                return
            elif text.lower().startswith("!mod"):
                moderator_service.insert_moderator(chat_id, text, from_user_id)
                return
            elif text.lower().startswith("!unmod"):
                moderator_service.remove_moderator(chat_id, text, from_user_id)
                return
            elif text.lower().startswith("!mute"):
                timeout_service.insert_timeout_user(chat_id, text, from_user_id)
                return
            elif text.lower().startswith("!unmute"):
                timeout_service.remove_timeout_user(chat_id, text, from_user_id)
                return
            elif text.lower().startswith("!add"):
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
            elif text.lower().startswith("!del"):
                custom_command_service.remove_command(chat_id, text, from_user_id)
                return
            elif (
                len(text) >= 3
                and not text.lower().startswith("!track")
                and not text.lower().startswith("!untrack")
            ):
                custom_command = text.split(" ", 0)[0].split("!")[1].lower()
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

        if text.lower().startswith("!track"):
            sale_tracker_keyword_service.insert_sale_tracker_keyword(
                chat_id, text, from_user_id, is_group
            )
        elif text.lower().startswith("!untrack"):
            sale_tracker_keyword_service.remove_sale_tracker_keyword(
                chat_id, text, from_user_id, is_group
            )

    except Exception as ex:
        syslog.create_warning("resolve_action", ex)
