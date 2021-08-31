from src.repositories.database import database
from src.services import (
    message_service,
    user_service,
    moderator_service,
    timeout_service,
)

# create tables if not exists
database.create_tables()

# get current users on database
user_service.get_all()
moderator_service.get_all()

updates = message_service.get_updates(0)
offset = 0 if len(updates) == 0 else message_service.get_last_update_id(updates) + 1

while True:
    updates = message_service.get_updates(offset)
    try:
        message_service.delete_messages(updates, timeout_service.timeout_users)

        if updates != None and len(updates) > 0:

            for update in updates:
                try:
                    message = update["message"]

                    if message:
                        message_service.resolve_action(message)
                except:
                    continue
    finally:
        offset = message_service.get_last_update_id(updates) + 1
