from src.repositories.database import database
from src.services import (
    message_service,
    user_service,
    moderator_service,
    timeout_service,
    custom_command_service,
    response_service,
)

print("→ starting telegrambot")

# create tables if not exists
print("→ creating tables if not exists... ", end="")
database.create_tables()
print("done!")

# get current users on database
print("→ get all objects from tables... ", end="")
user_service.get_all()
moderator_service.get_all()
custom_command_service.get_all()
print("done!")

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

print("telegrambot has ended")
