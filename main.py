import threading
import time
import os
from src.helpers.logging_helper import SystemLogging
from src.repositories.database import database
from src.services.app import api_listener_service, sale_tracker_service
from src.services import (
    user_service,
    moderator_service,
    custom_command_service,
    tracked_sale_service,
    keyword_service,
)

main_syslog = SystemLogging(__name__)


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def load_prerequisites(attempts: int = 0):
    total_attempts = attempts
    try:
        cls()
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
        tracked_sale_service.get_all_tracked_sales()
        keyword_service.get_all_keywords()
        print("done!")
    except Exception as ex:
        if total_attempts <= 3:
            total_attempts += 1
            time_in_seconds = total_attempts * 10
            print(
                f"an error occurred. waiting {time_in_seconds} seconds to try again..."
            )
            time.sleep(time_in_seconds)
            load_prerequisites(total_attempts)
        else:
            main_syslog.create_warning("start_bot", ex)
            print("could not start application. please check the log file")
            exit()


def main():
    load_prerequisites()

    print("→ starting sale tracker thread... ", end="")
    t1 = threading.Thread(target=sale_tracker_service.run_sale_tracker)
    t1.start()
    print("done!")

    print("→ starting api listener thread... ", end="")
    t2 = threading.Thread(target=api_listener_service.run_api_listener)
    t2.start()
    print("done!")


if __name__ == "__main__":
    main()
