import logging
import os
import re

from dotenv import load_dotenv
import pandas as pd
from slack_bolt import App

from utils.file import load_json

logging.basicConfig(level=logging.INFO)
load_dotenv()

tftbot = App(
    signing_secret=os.getenv("TFTBOT_SS"),
    token=os.getenv("TFTBOT_TOKEN"),
)


@tftbot.event("message")
def message_event(ack, event, logger, say):
    logger.info(event)
    if event.get("subtype"):
        ack()
    else:
        name = event.get("text")

        re_odds = re.match(pattern=r"^%\s*([1-9]|1[01])?$", string=name, flags=re.I)
        if re_odds:
            odds = pd.DataFrame(
                {
                    "1": [
                        "100%",
                        "100%",
                        "75%",
                        "55%",
                        "45%",
                        "30%",
                        "19%",
                        "17%",
                        "15%",
                        "5%",
                        "1%",
                    ],
                    "2": [
                        "0%",
                        "0%",
                        "25%",
                        "30%",
                        "33%",
                        "40%",
                        "30%",
                        "24%",
                        "18%",
                        "10%",
                        "2%",
                    ],
                    "3": [
                        "0%",
                        "0%",
                        "0%",
                        "15%",
                        "20%",
                        "25%",
                        "40%",
                        "32%",
                        "25%",
                        "20%",
                        "12%",
                    ],
                    "4": [
                        "0%",
                        "0%",
                        "0%",
                        "0%",
                        "2%",
                        "5%",
                        "10%",
                        "24%",
                        "30%",
                        "40%",
                        "50%",
                    ],
                    "5": [
                        "0%",
                        "0%",
                        "0%",
                        "0%",
                        "0%",
                        "0%",
                        "1%",
                        "3%",
                        "12%",
                        "25%",
                        "35%",
                    ],
                },
                index=[
                    "lev1",
                    "lev2",
                    "lev3",
                    "lev4",
                    "lev5",
                    "lev6",
                    "lev7",
                    "lev8",
                    "lev9",
                    "lev10",
                    "lev11",
                ],
            )

            lev = re_odds.group(1)
            if lev:
                result = odds.loc["lev" + lev].to_string()
            else:
                result = odds.to_string()
            say(f"```{result}```")

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
            champ_list = ", ".join(data.keys())
            say(champ_list)

        if name in data.keys():
            images = data.get(name)

            elems = []
            for image_src, image_alt in images:
                elems.append(
                    {
                        "type": "image",
                        "image_url": image_src,
                        "alt_text": image_alt,
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
