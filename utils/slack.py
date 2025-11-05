from logging.config import fileConfig
import logging
import os

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


load_dotenv()
slagger = logging.getLogger(name="slack_sdk.web.base_client")
slagger.disabled = 1


def slack_message(
    passw: str,
    delete: None | bool = None,
    private: None | bool = None,
    reactions: None | bool = None,
    timing: None | bool = None,
    **kwargs,
) -> None:
    fileConfig(os.path.expanduser("~/logs/logging.conf"))
    logger = logging.getLogger("slack-")
    client = WebClient(token=passw)

    try:
        if private:
            response = client.chat_postEphemeral(**kwargs)
        elif reactions:
            response = client.reactions_get(**kwargs)
            return response["message"].get("reactions")
        elif delete:
            response = client.chat_delete(**kwargs)
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
            slack_message(
                passw=os.getenv("WATCHER_TOKEN"),
                channel=os.getenv("SANDBOX_CHANNEL"),
                text=log,
            )
