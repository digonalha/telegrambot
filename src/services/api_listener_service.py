from src.services import timeout_service, message_service, response_service


def run_api_listener() -> None:
    """Loop for make requests to telegram api."""
    updates = message_service.get_updates(0)
    offset = 0 if len(updates) == 0 else message_service.get_last_update_id(updates) + 1

    print("→ listening for updates...")

    while True:
        updates = message_service.get_updates(offset)
        try:
            message_service.delete_messages(updates, timeout_service.timeout_users)

            if updates != None and len(updates) > 0:
                for update in updates:
                    try:
                        message = update["message"]

                        if message:
                            response_service.resolve_action(message)
                    except Exception:
                        continue
        finally:
            offset = message_service.get_last_update_id(updates) + 1
