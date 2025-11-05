import os
from random import choice
from time import sleep

from dotenv import load_dotenv

from utils.slack import slack_message


load_dotenv()
BOT = os.getenv("DOZAR_TOKEN")
CHANNEL = os.getenv("DOZAR_CHANNEL")


quotes = [
    "Did you bring me meat?",
    "Feed me!",
    "First, you feed me. Second, you feed me again. Capeesh?",
    "Me hungie :smiley_cat:",
    "Meow meow meow.. I can keep going.",
    "MMMEEEOOOOOOOOOOOOOWW!!",
    "I require sustenance peasants. See to it at once!",
    "Want me to plop? You know what to do.",
    "Who is going to feed me? :simple_smile:",
    "You feed me or I feed on you.. your choice.",
    "You wouldn't like me when I'm angry.",
]

reminders = [
    "AHEM!",
    "Anyone home?",
    "Curse those magic screens!",
    "Did you forget about me? :pleading_face:",
    "Food?",
    "Getting hangry...",
    "Hello?",
    "Meow.",
    "Still waiting...",
]


def dozar_was_fed(ts: str) -> bool:
    emojis = slack_message(
        reactions=True,
        passw=BOT,
        channel=CHANNEL,
        timestamp=ts,
    )
    if emojis:
        for emoji in emojis:
            if (
                emoji.get("name") is not None
                and emoji.get("name") == "white_check_mark"
            ):
                return True

    return False


def main() -> None:
    genesis = slack_message(
        timing=True,
        passw=BOT,
        channel=CHANNEL,
        text=choice(quotes),
    )

    minutes = 15
    timestamps = []
    dozar_is_still_hungry = True
    while dozar_is_still_hungry:
        sleep(minutes * 60)

        if dozar_was_fed(ts=genesis):
            dozar_is_still_hungry = False

        else:
            epoch = slack_message(
                timing=True,
                passw=BOT,
                icon_url="https://ik.imagekit.io/eetmbg795/doz1.png",
                username="Doz (reminder)",
                channel=CHANNEL,
                text=choice(reminders),
            )

            timestamps.append(epoch)

    for timestamp in timestamps:
        slack_message(
            delete=True,
            passw=BOT,
            channel=CHANNEL,
            ts=timestamp,
        )


if __name__ == "__main__":
    main()
