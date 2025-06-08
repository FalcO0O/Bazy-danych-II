import logging
from logging.handlers import TimedRotatingFileHandler

# Prosty logger do pliku
logger = logging.getLogger("auction_app")
logger.setLevel(logging.INFO)

# Rotacja co 1 dzień (tworzy plik logs.log.YYYY-MM-DD)
handler = TimedRotatingFileHandler("logs.log", when="midnight", interval=1)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
