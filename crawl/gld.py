from dotenv import load_dotenv
import logging
import logging.config
import json
import os

from curl_cffi import requests

load_dotenv(os.path.expanduser("~/python/.env"))
logging.config.fileConfig(os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("gl-gld")


def save(data) -> None:
    logger.info("saving file...")
    with open(
        file=os.path.expanduser("~/data/gld.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)
        logger.info("file saved")


def load() -> None:
    logger.info("retrieving data...")
    response = requests.get(
        url=os.getenv("URL_GLD"),
        impersonate="chrome",
    )
    if response.status_code == 200:
        logger.info("returned status code %s", response.status_code)
        save(data=response.json())
    else:
        logger.warning("returned status code %s", response.status_code)
        exit(response.status_code)


def main() -> None:
    logger.info("now running...")
    load()
    logger.info("completed")


if __name__ == "__main__":
    main()
