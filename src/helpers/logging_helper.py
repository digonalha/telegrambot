import logging
import traceback
from src.helpers import log_channel_helper


class SystemLogging:
    name: str

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)

        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler("info.log")
        console_handler.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.WARNING)

        console_handler.setFormatter(
            logging.Formatter("  → %(levelname)s | %(name)s | %(message)s")
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s | %(name)s | %(message)s")
        )

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def create_warning(
        self, function_name: str, error, user_id: int = 0, message_text: str = None
    ):
        str_traceback = None

        if not type(error) == str:
            str_traceback = "".join(
                traceback.format_exception(
                    etype=type(error),
                    value=error,
                    tb=error.__traceback__,
                )
            )

        error_msg = f"Warning, an exception occurred during execution\n\n"
        if user_id != 0:
            error_msg += f"*User id:*  `{user_id}`\n"
        if message_text:
            error_msg += f"*User message:*  `{message_text}`\n"
        error_msg += f"*Module:*  `{self.name}`\n"
        error_msg += f"*Function:*  `{function_name}`\n"
        error_msg += f"*Error:*  `{error}` \n"

        if str_traceback:
            error_msg += f"\_\_\_\_\_\_\_\_\_\_\_\n"
            error_msg += f"*Traceback:*\n`{str_traceback}`\n"

        self.logger.warning(error)
        log_channel_helper.send_alert_log_channel(error_msg)

    def create_info(self, function_name: str, message: str):
        self.logger.info(f"success on function <{function_name}>: {message}")
