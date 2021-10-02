import threading
from src.repositories.database import database
from src.services import (
    api_listener_service,
    sale_monitor_service,
    user_service,
    moderator_service,
    custom_command_service,
)

print("→ starting telegrambot")

# create tables if not exists
print("→ creating tables if not exists... ", end="")
database.create_tables()
print("done!")

# get current users on database
print("→ get all objects from tables... ", end="")
user_service.get_all_users()
moderator_service.get_all_moderators()
custom_command_service.get_all_commands()
print("done!")


def main():
    print("→ starting sale monitor thread... ", end="")
    t1 = threading.Thread(target=sale_monitor_service.run_sale_monitor)
    t1.start()
    print("done!")

    print("→ starting api listener thread... ", end="")
    t2 = threading.Thread(target=api_listener_service.run_api_listener)
    t2.start()
    print("done!")


if __name__ == "__main__":
    main()
