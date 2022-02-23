import os
from dotenv import load_dotenv

connection_string = None
api_token = None
bot_name = None
max_commands = 10
max_keywords = 10
promo_version = None
error_log_channel = None
promobot_channel = None


def load():
    try:
        load_dotenv()

        global connection_string, api_token, bot_name, max_commands, max_keywords, promo_version, error_log_channel, promobot_channel

        connection_string = os.getenv("CONNECTION_STRING")
        api_token = os.getenv("API_TOKEN")
        bot_name = os.getenv("BOT_NAME")
        max_commands = os.getenv("MAX_COMMANDS")
        max_keywords = os.getenv("MAX_KEYWORDS")
        promo_version = os.getenv("PROMO_VERSION")
        error_log_channel = os.getenv("ERROR_LOG_CHANNEL")
        promobot_channel = os.getenv("PROMOBOT_CHANNEL")

        if not connection_string:
            raise Exception("cant find connection_string. check your .env file")
        elif not api_token:
            raise Exception("cant find api_token. check your .env file")
        elif not bot_name:
            raise Exception("cant find bot_name. check your .env file")
        elif not promo_version:
            raise Exception("cant find promo_version. check your .env file")
        elif not error_log_channel:
            raise Exception("cant find error_log_channel. check your .env file")
        elif not promobot_channel:
            raise Exception("cant find promobot_channel. check your .env file")

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
        print(ex)
        exit()


load()
