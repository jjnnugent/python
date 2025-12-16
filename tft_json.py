import logging
from logging.config import fileConfig
import json
import os
import re

from curl_cffi import requests
from utils.file import save_json
from utils.slack import SlackHandler


def filter_data(data: dict) -> dict:
    queries = (
        data.get("props", {})
        .get("pageProps", {})
        .get("dehydratedState", {})
        .get("queries", {})
    )

    for i in range(len(queries)):
        sel = queries[i].get("state", {}).get("data", {})
        if i == 0:
            champs = sel.get("champions")
        elif i == 2:
            items = sel.get("items")
        elif i == 3:
            comps = sel.get("guideDecks")
        else:
            continue

    if champs is None or items is None or comps is None:
        logger.warning(
            "champs(%s) items(%s) comps(%s) not found",
            bool(champs),
            bool(items),
            bool(comps),
        )
        exit()

    filtered_data = dict()
    for champ in champs:
        champ_alt = champ.get("name")
        champ_img = champ.get("imageUrl")
        champ_name = champ.get("key").lower()

        bis_images = []
        bis_items = champ.get("recommendItems")
        if bis_items:
            for bis_item in bis_items:
                for item in items:
                    item_key = item.get("ingameKey")
                    if item_key == bis_item:
                        item_alt = item.get("name")
                        item_src = item.get("imageUrl")
                        bis_images.append(
                            [
                                item_src
                                if item_src.startswith("https:")
                                else "https:" + item_src,
                                item_alt,
                            ]
                        )

            filtered_data[champ_name] = {
                "alt": champ_alt,
                "bis": bis_images,
                "src": champ_img
                if champ_img.startswith("https:")
                else "https:" + champ_img,
            }

    team_comps = list()
    for comp in comps:
        slots = comp.get("data", {}).get("slots", {})

        team = list()
        for slot in slots:
            comp_champ = slot.get("champion")
            if comp_champ:
                comp_champ = comp_champ.lower()
                if comp_champ in ["azirultsoldier", "freljordprop"]:
                    continue
                else:
                    team.append(comp_champ)

        team_comps.append(team)

    filtered_data["comps"] = team_comps
    return filtered_data


if __name__ == "__main__":
    fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
    logger = logging.getLogger("gettft")
    logger.addHandler(hdlr=SlackHandler())

    response = requests.get(url=os.getenv("URL_TF"), impersonate="chrome")
    if response.status_code == 200:
        re_json = re.search(
            pattern=r"\"__NEXT_DATA__\".*?\>([^<]+)\<", string=response.text, flags=re.I
        )

        if re_json:
            json_data = json.loads(re_json.group(1))
            tft_data = filter_data(data=json_data)
            save_json(data=tft_data, name=os.path.expanduser("~/data/tft.json"))
        else:
            logger.warning("data not found")
    else:
        logger.warning("%s returned", response.status_code)
