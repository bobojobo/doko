import logging
from doko._settings import _Settings

settings = _Settings()
logging.basicConfig(level=settings.DEBUG_LEVEL)
logging.info(f"Initializing with the folling settings: \n{settings}")
