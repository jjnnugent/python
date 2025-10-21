from random import choice
import os

from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv(os.path.expanduser("~/python/.env"))
# slagger = logging.getLogger(name="slack_sdk.web.base_client")
# slagger.disabled = 1

# fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
# logger = logging.getLogger("------")


def slack_message() -> None:
    quotes = [
        "Get off your lazy asses and feed me!",
        "Meow meow meow.. I can keep going...",
        "Me hungie :smiley_cat:",
        "You wouldn't like me when I'm angry.",
        "Did you bring me meat?",
        "I require sustenance peasants. See to it at once!",
        "You feed me or I feed on you.. you're choice.",
        "MMMEEEOOOOOOOOOWW!!",
        "I gets then I sits.",
        "First, you feed me. Second, you feed me again. Capeesh?",
    ]

    client = WebClient(token=os.getenv("DOZAR_TOKEN"))
    response = client.chat_postMessage(
        channel=os.getenv("DOZAR_CHANNEL"),
        # icon_url="https://ik.imagekit.io/eetmbg795/doz1.png",
        text=choice(quotes),
    )


def main() -> None:
    slack_message()


if __name__ == "__main__":
    main()
