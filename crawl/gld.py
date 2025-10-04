from logging.config import fileConfig
import logging
import logging.config
import json
import os

from curl_cffi import requests
from dotenv import load_dotenv
from json.decoder import JSONDecodeError
from slack_sdk import WebClient

load_dotenv(os.path.expanduser("~/python/.env"))
fileConfig(os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("gl-gld")
slagger = logging.getLogger(name="slack_sdk.web.base_client")
slagger.disabled = 1


def save(data) -> None:
    with open(
        file=os.path.expanduser("~/data/gld.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)
    logger.info("gld.json saved")


def slack_message(message: str) -> None:
    client = WebClient(token=os.getenv("WATCHER_TOKEN"))
    sent = client.chat_postMessage(
        channel=os.getenv("SANDBOX_CHANNEL"),
        text=message,
    )
    if not sent:
        logger.warning("slack message failed")


def main() -> None:
    result = ""
    response = requests.get(
        url=os.getenv("URL_GLD"),
        impersonate="chrome",
    )
    if response.status_code == 200:
        try:
            result = response.json()
        except JSONDecodeError as e:
            logger.error(e)
        if result:
            save(result)
        else:
            slack_message(message="[WARNING] GLD no data found")
    else:
        logger.warning("returned status code %s", response.status_code)


if __name__ == "__main__":
    main()
