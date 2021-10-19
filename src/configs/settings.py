import os
from dotenv import load_dotenv
from src.helpers.logging_helper import SystemLogging

syslog = SystemLogging(__name__)

connection_string = None
api_token = None
bot_name = None
max_commands = 10
max_keywords = 10
promo_version = None


def load():
    try:
        load_dotenv()

        global connection_string, api_token, bot_name, max_commands, max_keywords, promo_version

        connection_string = os.getenv("CONNECTION_STRING")
        api_token = os.getenv("API_TOKEN")
        bot_name = os.getenv("BOT_NAME")
        max_commands = os.getenv("MAX_COMMANDS")
        max_keywords = os.getenv("MAX_KEYWORDS")
        promo_version = os.getenv("PROMO_VERSION")

        if not connection_string:
            raise Exception("cant find connection string. check your .env file")
        elif not api_token:
            raise Exception("cant find api token. check your .env file")
        elif not bot_name:
            raise Exception("cant find bot name. check your .env file")
        elif not promo_version:
            raise Exception("cant find promo version. check your .env file")

        max_commands = (
            10
            if not max_commands or not max_commands.isnumeric()
            else int(max_commands)
        )

        max_keywords = (
            10
            if not max_keywords or not max_keywords.isnumeric()
            else int(max_keywords)
        )

    except Exception as ex:
        syslog.create_warning("load", ex)
        exit()


load()
