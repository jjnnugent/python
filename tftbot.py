import logging
import os
import re

from dotenv import load_dotenv
from slack_bolt import App

from utils.file import load_json

logging.basicConfig(level=logging.INFO)
load_dotenv()

tftbot = App(
    signing_secret=os.getenv("TFTBOT_SS"),
    token=os.getenv("TFTBOT_TOKEN"),
)


@tftbot.event("message")
def message_event(event, logger, say):
    logger.info(event)
    if not event.get("subtype"):
        name = event.get("text")
        if name == "sol":
            name = "aurelionsol"
        if name == "baron" or name == "nashor":
            name = "baronnashor"
        if name == "blitz":
            name = "blitzcrank"
        if name == "cho":
            name = "chogath"
        if name.startswith("dr"):
            name = "drmundo"
        if name == "gp":
            name = "gangplank"
        if name.startswith("il"):
            name = "illaoi"
        if name == "jarvan":
            name = "jarvaniv"
        if name == "kobuko" or name == "yuumi":
            name = "kobukoyuumi"
        if name.startswith("malz"):
            name = "malzahar"
        if name == "mf":
            name = "missfortune"
        if name == "lucian" or name == "senna":
            name = "luciansenna"
        if name == "nut":
            name = "nautilus"
        if name.startswith("qu") or name == "yana":
            name = "quiyana"
        if name == "rift" or name == "harold":
            name = "riftherald"
        if name.startswith("sej"):
            name = "sejuani"
        if name.startswith("tom") or name.startswith("tahm"):
            name = "tahmkench"
        if name.startswith("try"):
            name = "tryndamere"
        if name == "tf":
            name = "twistedfate"
        if name.startswith("xin"):
            name = "xinzhao"

        data = load_json(os.path.expanduser("~/data/tft.json"))

        if name == "list":
            champ_list = str(data.keys())
            say(champ_list)

        if name in data.keys():
            images = data.get(name)

            elems = []
            for src in images:
                elems.append(
                    {
                        "type": "image",
                        "image_url": src,
                        "alt_text": "",
                    }
                )

            block = [
                {
                    "type": "context",
                    "elements": elems,
                }
            ]

            say(text=f"{name} bis", blocks=block)


if __name__ == "__main__":
    tftbot.start(port=52259)
