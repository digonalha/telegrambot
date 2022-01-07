import abc
from repositories.models.command_model import MediaType
from helpers.logging_helper import SystemLogging
from helpers import string_helper
from configs import settings
from services import (
    user_service,
    moderator_service,
    timeout_service,
    command_service,
    message_service,
    keyword_service,
    sale_service,
)


syslog = SystemLogging(__name__)


def send_commands_message(chat_id: int, name: str, message_id: int):
    """Send a list of custom commands when asked on chat."""
    messages = ""

    command_service.commands.sort(key=lambda x: x.command)

    total_commands = 0

    for cc in command_service.commands:
        if cc.chat_id == chat_id:
            total_commands += 1
            description = "Nenhuma descrição encontrada"

            if cc.description and len(cc.description) > 0:
                description = cc.description

            messages += f"*/{cc.command}* - {description}\n"

    if len(messages) == 0:
        message_service.send_message(
            chat_id,
            "Nenhum comando customizado encontrado para o grupo. Utilize o comando */addcmd* para cadastrar novos comandos",
        )
        return

    help_message = (
        f"Olá, *{(name)}*!\n"
        "Aqui estão os comandos customizados disponíveis no grupo:\n\n"
        f"{messages}"
        f"\n*Total: {str(total_commands)}/{str(settings.max_commands)}*"
    )

    message_service.send_message(chat_id, help_message)


def send_group_help_message(chat_id: int, name: str, message_id: int) -> None:
    """Send help message when asked on chat."""

    help_message = (
        f"Olá, *{(name)}*!\n"
        "Aqui estão os meus comandos disponíveis:\n\n"
        "*/help* - lista os comandos disponíveis\n"
        "*/mod* `username` - promove o usuário ao cargo de moderador \*\n"
        "*/unmod* `username` - rebaixa o usuário do cargo de moderador \*\n"
        "*/mute* `username | tempo_em_segundos` - adiciona o usuário na lista de silenciados pelo tempo especificado \*\*\n"
        "*/unmute* `username` - remove o usuário da lista de silenciados \*\*\n"
        "*/cmd* - lista os comandos customizados disponíveis no grupo\n"
        "*/addcmd* `comando | resposta | descrição` - adiciona um novo comando (para mídias, enviar o comando na legenda) \*\*\n"
        "*/delcmd* `comando` - remove um comando customizado \*\n\n"
        "\* _necessário ser um administrador_\n"
        "\*\* _necessário ser um administrador ou moderador_\n\n"
        "Eu também tenho um canal onde posto promoções. Acesse pelo link: https://t.me/promobotcanal"
        f"\n\nPara monitorar promoções de um produto especifico, envie /help no privado para @{settings.bot_name}"
    )

    message_service.send_message(
        chat_id, help_message, reply_id=message_id, disable_web_page_preview=True
    )


def send_private_help_message(chat_id: int, name: str) -> None:
    help_message = (
        f"Olá, *{(name)}*!\n"
        "Aqui estão os meus comandos disponíveis:\n\n"
        "*/help* - lista os comandos disponíveis\n"
        "*/promo* - lista as promoções monitoradas pelo usuário\n"
        "*/lastpromo* `palavra-chave` - retorna as promoções das últimas 24 horas relacionadas à palavra-chave\n"
        "*/addpromo* `palavra-chave | valor-máx` - adiciona a palavra-chave na lista de monitoramento de promoções do usuário\n"
        "*/delpromo* `palavra-chave` - remove a palavra-chave da lista de monitoramento de promoções do usuário\n"
        "*/clearpromo* - remove todas as palavras-chave da lista de monitoramento de promoções\n\n"
        "Eu também tenho um canal onde posto promoções. Acesse pelo link: https://t.me/promobotcanal"
    )

    message_service.send_message(chat_id, help_message, disable_web_page_preview=True)


def resolve_callback(callback_query) -> None:
    try:
        from_user_id = callback_query["from"]["id"]
        message_id = callback_query["message"]["message_id"]

        keyword_to_search = {"keyword": "", "max_price": ""}

        callback_data = callback_query["data"]

        sale_service.check_last_sales(
            from_user_id,
            keyword_to_search,
            callback_data=callback_data,
            message_id=message_id,
            callback_id=callback_query["id"],
        )
    except Exception as ex:
        syslog.create_warning("resolve_callback", ex, from_user_id, callback_data)


def resolve_message(message) -> None:
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

        # sanitize text:
        text = string_helper.string_sanitize(text)

        is_group = message["chat"]["type"] == "group"

        if is_group:
            if text.lower() == "/help" or (
                settings.bot_name and text.lower() == f"/help@{settings.bot_name}"
            ):
                send_group_help_message(
                    chat_id, message["from"]["first_name"], message["message_id"]
                )
                return
            elif text.lower() == "/cmd" or (
                settings.bot_name and text.lower() == f"/cmd@{settings.bot_name}"
            ):
                send_commands_message(
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
                    if len(message["photo"]) == 3:
                        file_id = message["photo"][2]["file_id"]
                    elif len(message["photo"]) == 2:
                        file_id = message["photo"][1]["file_id"]
                    else:
                        file_id = message["photo"][0]["file_id"]
                    media_type = MediaType.IMAGE
                elif "animation" in message:
                    file_id = message["animation"]["file_id"]
                    media_type = MediaType.ANIMATION
                elif "video" in message:
                    file_id = message["video"]["file_id"]
                    media_type = MediaType.VIDEO

                command_service.insert_command(
                    chat_id, text, from_user_id, file_id, media_type
                )

                return
            elif text.lower().startswith("/delcmd"):
                command_service.remove_command(chat_id, text, from_user_id)
                return
            elif len(text) >= 3:
                command = text.split(" ", 0)[0].split("/")[1].lower()

                if settings.bot_name and f"@{settings.bot_name}" in command:
                    command = command.split(f"@{settings.bot_name}")[0]

                db_command = command_service.get_command(command, chat_id)

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
                    elif db_command.media_type == MediaType.VIDEO:
                        message_service.send_video(chat_id, db_command.file_id)
                    else:
                        message_service.send_message(chat_id, db_command.text)
                return
        else:
            if text.lower() == "/help" or text.lower() == "/start":
                send_private_help_message(chat_id, message["from"]["first_name"])
            elif text.lower() == "/promo":
                keyword_service.get_user_keywords(chat_id)
            elif text.lower().startswith("/lastpromo"):
                keyword_service.get_last_sales_by_keyword(chat_id, text)
            elif text.lower().startswith("/clearpromo"):
                keyword_service.remove_all_keywords(chat_id, text)
            elif text.lower().startswith("/addpromo"):
                keyword_service.insert_keyword(chat_id, text)
            elif text.lower().startswith("/delpromo"):
                keyword_service.remove_keyword(chat_id, text)

    except Exception as ex:
        syslog.create_warning("resolve_message", ex, chat_id, text)
