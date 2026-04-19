import logging

logger = logging.getLogger("my_cli_app")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)

file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")
file_handler.setFormatter(file_formatter)

if not logger.handlers:
  logger.addHandler(file_handler)