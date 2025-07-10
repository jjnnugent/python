from logging.config import fileConfig
import logging
import logging.config
import json
import os

from curl_cffi import requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/python/.env"))
fileConfig(os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("gl-gld")


def save(data) -> None:
    with open(
        file=os.path.expanduser("~/data/gld.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)
    logger.info("gld.json saved")


def main() -> None:
    response = requests.get(
        url=os.getenv("URL_GLD"),
        impersonate="chrome",
    )
    if response.status_code == 200:
        save(data=response.json())
    else:
        logger.warning("returned status code %s", response.status_code)


if __name__ == "__main__":
    main()
