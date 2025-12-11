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
def message_event(ack, client, event, logger, say):
    logger.info(event)
    if event.get("subtype"):
        ack()
    else:
        channel_id = event.get("channel")
        name = event.get("text")
        user_id = event.get("user")

        re_odds = re.match(pattern=r"^%\s*([1-9]|1[01])?\*?$", string=name, flags=re.I)
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
                        "15%",
                        "10%",
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
                        "20%",
                        "17%",
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
                        "30%",
                        "33%",
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
                        "15%",
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
            if lev and name.endswith("*"):
                num = int(lev)
                rows = odds.to_string().split("\n")

                result = str()
                for i in range(len(rows)):
                    if i == num:
                        result += "\n" + "-" * len(rows[i])
                    result += "\n" + rows[i]
                    if i == num:
                        result += "\n" + "-" * len(rows[i])
            elif lev:
                num = int(lev)
                result = odds.loc[["lev" + lev]].to_string()
            else:
                result = odds.to_string()

            # say(f"```{result}```")
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=f"```{result}```",
            )

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

        if name == "champs" or name == "list":
            champ_list = ", ".join(data.keys())
            # say(champ_list)
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=champ_list,
            )

        elif name in data.keys():
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

            bis_block = [
                {
                    "type": "context",
                    "elements": elems,
                }
            ]

            comp_block = list()
            for comp in data["comps"]:
                if name in comp:
                    comp_block.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "plain_text",
                                "text": ", ".join(comp),
                                "emoji": False,
                            },
                        }
                    )

            # say(text=f"{name} bis", blocks=block)
            block = bis_block + comp_block
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                blocks=block,
                text=name,
            )


if __name__ == "__main__":
    tftbot.start(port=52259)
