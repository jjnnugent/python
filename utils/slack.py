from logging.config import fileConfig
from typing import Optional
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
                channel_id=os.getenv("SANDBOX_CHANNEL"),
                message=log,
            )


def slack_message(
    passw: str,
    channel_id: str,
    message: str,
    user_id: Optional[str] = None,
    block: Optional[list] = None,
    links: Optional[bool] = None,
    media: Optional[bool] = None,
    private: Optional[bool] = None,
    timing: Optional[bool] = None,
) -> None | str:
    client = WebClient(token=passw)
    if private:
        response = client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text=message,
            blocks=block,
        )
    else:
        response = client.chat_postMessage(
            channel=channel_id,
            text=message,
            blocks=block,
            unfurl_links=links,
            unfurl_media=media,
        )

    if timing:
        return response["message"]["ts"]


def main():
    print("hello")


if __name__ == "__main__":
    main()
