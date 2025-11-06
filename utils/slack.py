from logging.config import fileConfig
import logging
import os

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def slack_message(
    passw: str,
    delete: None | bool = None,
    private: None | bool = None,
    reactions: None | bool = None,
    timing: None | bool = None,
    update: None | bool = None,
    **kwargs,
) -> None:
    client = WebClient(token=passw)

    fileConfig(os.path.expanduser("~/logs/logging.conf"))
    slagger = logging.getLogger(name="slack_sdk.web.base_client")
    slagger.disabled = 1
    logger = logging.getLogger("slack-")

    try:
        if private:
            response = client.chat_postEphemeral(**kwargs)
        elif reactions:
            response = client.reactions_get(**kwargs)
            return response["message"].get("reactions")
        elif delete:
            response = client.chat_delete(**kwargs)
        elif update:
            response = client.chat_update(**kwargs)
        else:
            response = client.chat_postMessage(**kwargs)

        if timing:
            return response["message"].get("ts")

    except SlackApiError as e:
        logger.error("%s %s", kwargs, e)


class SlackHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.WARNING:
            name = record.name
            msg = record.getMessage()
            sev = record.levelname[:4]
            log = f"{name} {msg} [{sev}]"

            load_dotenv()
            slack_message(
                passw=os.getenv("WATCHER_TOKEN"),
                channel=os.getenv("SANDBOX_CHANNEL"),
                text=log,
            )
