# from logging.config import fileConfig
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
    upload: None | bool = None,
    **kwargs,
) -> None:
    client = WebClient(token=passw)

    # fileConfig(os.path.expanduser("~/logs/logging.conf"))
    slogger = logging.getLogger("slack-")
    slagger = logging.getLogger(name="slack_sdk.web.base_client")
    slagger.disabled = 1

    try:
        if upload:
            response = client.files_upload_v2(**kwargs)
        elif update:
            response = client.chat_update(**kwargs)
        elif private:
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
        slogger.error("%s %s", kwargs, e)


class SlackHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.WARNING:
            name = record.name
            msg = record.getMessage()
            sev = record.levelname
            log = f"{name} {msg} [{sev}]"

            # slagger = logging.getLogger(name="slack_sdk.web.base_client")
            # slagger.disabled = 1

            load_dotenv()
            slack_message(
                passw=os.getenv("WATCHER_TOKEN"),
                channel=os.getenv("SANDBOX_CHANNEL"),
                text=log,
            )
