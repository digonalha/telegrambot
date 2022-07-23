import threading
import time
import os

from app.services import (
    sale_tracker_app_service,
    telegram_app_service,
    correios_app_service,
)
from data.database import database
from shared.helpers.logging_helper import SystemLogging
from domain.services import (
    user_service,
    moderator_service,
    command_service,
    sale_service,
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
        command_service.get_all_commands()
        sale_service.get_last_day_sales()
        keyword_service.get_all_keywords()
        print("done!")
    except Exception as ex:
        if total_attempts <= 50:
            total_attempts += 1
            time_in_seconds = total_attempts * 5
            print(
                f"an error occurred. waiting {time_in_seconds} seconds to try again..."
            )
            time.sleep(time_in_seconds)
            load_prerequisites(total_attempts)
        else:
            main_syslog.create_warning("load_prerequisites", ex)
            print("could not start application. please check the log file")
            exit()


def main():
    load_prerequisites()

    print("→ starting sale webscrap worker... ", end="")
    t1 = threading.Thread(target=sale_tracker_app_service.run_webscrap_worker)
    t1.start()
    print("done!")

    print("→ starting correios tracking worker... ", end="")
    t2 = threading.Thread(target=correios_app_service.run_tracking_worker)
    t2.start()
    print("done!")

    print("→ starting telegrambot worker... ", end="")
    t3 = threading.Thread(target=telegram_app_service.run_telegram_worker)
    t3.start()
    print("done!")


if __name__ == "__main__":
    main()
