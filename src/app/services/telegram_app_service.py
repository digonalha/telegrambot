from time import sleep
from app.services import response_app_service
from shared.helpers.logging_helper import SystemLogging
from domain.services import message_service, timeout_service

syslog = SystemLogging(__name__)


def run_telegram_worker() -> None:
    """Loop for make requests to telegram api."""
    print("→ listening for updates...")

    offset = 0

    while True:
        sleep(1)
        try:
            updates = message_service.get_updates(offset)
            offset = message_service.get_update_id_offset(updates)

            message_service.delete_messages(updates, timeout_service.timeout_users)

            if updates and len(updates) > 0:
                for update in updates:
                    request_obj = None
                    if "message" in update:
                        request_obj = update["message"]
                        response_app_service.resolve_message(request_obj)
                    elif "callback_query" in update:
                        request_obj = update["callback_query"]
                        response_app_service.resolve_callback(request_obj)

        except Exception as ex:
            syslog.create_warning("telegram_worker", ex)
            continue
