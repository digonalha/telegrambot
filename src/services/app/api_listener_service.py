from src.services import timeout_service, message_service, response_service


def run_api_listener() -> None:
    """Loop for make requests to telegram api."""
    updates = message_service.get_updates(0)
    offset = message_service.get_update_id_offset(updates)

    print("→ listening for updates...")

    while True:
        updates = message_service.get_updates(offset)
        try:
            message_service.delete_messages(updates, timeout_service.timeout_users)

            if updates and len(updates) > 0:
                for update in updates:
                    try:
                        message = update["message"]

                        if message:
                            response_service.resolve_action(message)
                    except Exception:
                        continue
        finally:
            offset = message_service.get_update_id_offset(updates)
