from src.helpers.logging_helper import SystemLogging
from src.services import (
    user_service,
    moderator_service,
    timeout_service,
    custom_command_service,
    message_service,
)

syslog = SystemLogging(__name__)

# def resolve_custom_command(message):
    


def resolve_action(message):
    try:
        message_from = message["from"]
        chat_id = message["chat"]["id"]

        if timeout_service.is_user_in_timeout(chat_id, message_from["id"]):
            return

        item_text = ""
        item_caption = ""

        # persistindo usuarios:
        user_service.add_user_if_not_exists(
            message_from["id"], message_from["username"]
        )

        if "text" in message:
            item_text = message["text"]
        elif "caption" in message:
            item_caption = message["caption"]
        if item_text.lower().startswith("!help"):
            message_service.send_help_message(
                chat_id, message_from["id"], message["message_id"]
            )
        elif item_text.lower().startswith("!mod"):
            moderator_service.insert_moderator(chat_id, item_text, message_from["id"])
        elif item_text.lower().startswith("!unmod"):
            moderator_service.remove_moderator(chat_id, item_text, message_from["id"])
        elif item_text.lower().startswith("!mute"):
            timeout_service.insert_timeout_user(chat_id, item_text, message_from["id"])
        elif item_text.lower().startswith("!unmute"):
            timeout_service.remove_timeout_user(chat_id, item_text, message_from["id"])
        elif item_text.lower().startswith(
            "!newcommand"
        ) or item_caption.lower().startswith("!newcommand"):
            text = item_text if item_caption == "" else item_caption
            custom_command_service.insert_custom_command(
                chat_id, text, message_from["id"]
            )
        elif item_text.startswith("!") or item_caption.startswith("!"):
            text = item_text if item_caption == "" else item_caption

            if text == "!":
                return

            custom_command = text.split(" ", 0)[0]
            custom_command = custom_command.split("!")[1]

            db_command = custom_command_service.get_command(custom_command, chat_id)

            if db_command:
                message_service.send_message(chat_id, db_command["text"])

    except Exception as ex:
        syslog.create_warning("resolve_action", ex)
