from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient
from dotenv import load_dotenv
from datetime import datetime
import os

import logging
from logging.config import fileConfig

slagger = logging.getLogger(name="slack_sdk.web.base_client")
slagger.disabled = 1

fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger(name="gl-tue")

load_dotenv(os.path.expanduser("~/python/.env"))
client = WebClient(token=os.getenv("WATCHER_TOKEN"))


def slack_message() -> None:
    now = datetime.now()
    date = str(now.date()).replace("-", "")
    fname = f"{date}_gld.csv"
    try:
        client.files_upload_v2(
            file=os.path.expanduser("~/data/gld.csv"),
            title=fname,
            channel=os.getenv("COOL_CHANNEL"),
            initial_comment="Gaming Laptop Deals"
        )
        logger.info("slack message sent")
    except SlackApiError as error:
        logger.error(error)


if __name__ == "__main__":
    slack_message()
