import logging
import os

from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv()


class SlackHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.CRITICAL:
            name = record.name
            msg = record.getMessage()
            sev = record.levelname[:4]
            log = f"{name} {msg} [{sev}]"
            slack_message(
                passw=os.getenv("WATCHER_TOKEN"),
                channel=os.getenv("SANDBOX_CHANNEL"),
                text=log,
            )


def slack_message(
    passw: str,
    delete: None | bool = None,
    private: None | bool = None,
    reactions: None | bool = None,
    timing: None | bool = None,
    **kwargs,
) -> None:
    client = WebClient(token=passw)

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
