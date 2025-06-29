from selectolax.parser import HTMLParser
from curl_cffi import requests
from dotenv import load_dotenv
import os

from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient

import logging
from logging.config import fileConfig

slagger = logging.getLogger(name="slack_sdk.web.base_client")
slagger.disabled = 1

fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("pjg---")
load_dotenv(os.path.expanduser("~/python/.env"))


def load() -> str:
    with open(
        file=os.path.expanduser("~/data/pjg.txt"), mode="r", encoding="utf-8"
    ) as file:
        return file.read()


def save(data: str) -> None:
    with open(
        file=os.path.expanduser("~/data/pjg.txt"), mode="w", encoding="utf-8"
    ) as file:
        file.write(data)
        logger.info("data saved '%s'", data)


def crawl() -> str | None:
    text = ""
    response = requests.get("https://japanesegarden.org/2025-cherry-blossom-watch/")
    if response.status_code == 200:
        tree = HTMLParser(response.content)
        text = tree.css_first("h2.wp-block-heading").text(strip=True)
        return text
    else:
        logger.warning("returned status code %s", response.status_code)
        exit(response.status_code)
    return None


def slack_message() -> bool:
    client = WebClient(token=os.getenv("WATCHER_TOKEN"))
    try:
        client.chat_postMessage(
            channel="D06G24QH97W",
            text="New cherry blossom update!\nhttps://japanesegarden.org/2025-cherry-blossom-watch/",
        )
        return True
    except SlackApiError as error:
        logger.error(error)
    return False


def main() -> None:
    old = load()
    new = crawl()
    if old == new:
        logger.info("no updates")
    else:
        save(new)
        sent = slack_message()
        if sent:
            logger.info("slack message sent")
        else:
            logger.error("something went wrong")


if __name__ == "__main__":
    main()
