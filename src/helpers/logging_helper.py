import logging


class SystemLogging:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler("info.log")
        console_handler.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.WARNING)

        console_handler.setFormatter(
            logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def create_warning(self, function_name: str, error):
        self.logger.warning(f"exception on function <{function_name}>: {error}")

    def create_info(self, function_name: str, message: str):
        self.logger.info(f"success on function <{function_name}>: {message}")
