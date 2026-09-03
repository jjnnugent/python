import logging
import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_sdk import WebClient
from utils import *


load_dotenv(os.path.expanduser("~/python/.env"))
logging.basicConfig(level=logging.DEBUG)
client = WebClient(token=os.getenv("MEESEEKS_TOKEN"))
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


@mr_meeseeks.command("/gas")
def command_gas(ack, command, respond) -> None:
    ack()

    # if command["text"] == "help":
    #     result = help(slash=command["command"])
    #     respond(text=result)
    # else:

    user_id = command.get("user_id")
    user_name = command.get("user_name")
    channel_id = command.get("channel_id")
    result = gas(user_id=user_id)

    block = [
        {
            "type": "markdown",
            "text": result
        }
    ]

    client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        blocks=block,
        text="best local gas prices"
    )

    if user_id != "U02S8PJP96H":

        client.chat_postMessage(
            channel=os.getenv("SANDBOX_CHANNEL"),
            blocks=block,
            text=f"{user_name} local gas prices"
        )


@ mr_meeseeks.command("/gld")
def command_gld(ack, command, respond) -> None:
    ack()
    if command["text"] == "help":
        result = help(slash=command["command"])
        respond(text=result)
    else:
        result = gld(text=command["text"])
        respond(response_type="ephemeral", text=result)


@ mr_meeseeks.command("/pm")
def command_pm(ack, command, respond) -> None:
    ack()
    if command["text"] == "help":
        result = help(slash=command["command"])
        respond(text=result)
    else:
        result = pm(text=command["text"])
        respond(response_type="ephemeral", text=result)


@ mr_meeseeks.command("/shop")
def command_shop(ack, command, respond) -> None:
    ack()
    if command["text"] == "help":
        result = help(slash=command["command"])
        respond(text=result)
    else:
        result = shop(text=command["text"])
        respond(response_type="ephemeral", unfurl_links=False, text=result)


@ mr_meeseeks.command("/zon")
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
