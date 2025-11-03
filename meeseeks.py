import logging
import os

from dotenv import load_dotenv
from slack_bolt import App
from utils import *

load_dotenv(os.path.expanduser("~/python/.env"))
logging.basicConfig(level=logging.DEBUG)

mr_meeseeks = App(
    signing_secret=os.getenv("MEESEEKS_SS"), token=os.getenv("MEESEEKS_TOKEN")
)


@mr_meeseeks.command("/altcaps")
def command_altcaps(ack, command, respond) -> None:
    ack()
    if command["text"] == "help":
        result = help(slash=command["command"])
        respond(text=result)
    else:
        result = altcaps(text=command["text"])
        respond(response_type="ephemeral", text=result)


@mr_meeseeks.command("/drive")
def command_drive(ack, command, respond) -> None:
    ack()
    if command["text"] == "help":
        result = help(slash=command["command"])
        respond(text=result)
    else:
        result = drive(text=command["text"])
        respond(response_type="ephemeral", unfurl_links=False, text=result)


@mr_meeseeks.command("/gld")
def command_gld(ack, command, respond) -> None:
    ack()
    if command["text"] == "help":
        result = help(slash=command["command"])
        respond(text=result)
    else:
        result = gld(text=command["text"])
        respond(response_type="ephemeral", text=result)


@mr_meeseeks.command("/pm")
def command_pm(ack, command, respond) -> None:
    ack()
    if command["text"] == "help":
        result = help(slash=command["command"])
        respond(text=result)
    else:
        result = pm(text=command["text"])
        respond(response_type="ephemeral", text=result)


@mr_meeseeks.command("/shop")
def command_shop(ack, command, respond) -> None:
    ack()
    if command["text"] == "help":
        result = help(slash=command["command"])
        respond(text=result)
    else:
        result = shop(text=command["text"])
        respond(response_type="ephemeral", unfurl_links=False, text=result)


@mr_meeseeks.command("/zon")
def command_zon(ack, command, respond) -> None:
    ack()
    if command["text"] == "help":
        result = help(slash=command["command"])
        respond(text=result)
    else:
        result = zon(text=command["text"])
        respond(response_type="ephemeral", text=result)


if __name__ == "__main__":
    mr_meeseeks.start(port=52257)
