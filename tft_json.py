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
    filtered_data["champs"] = {}
    for champ in champs:
        champ_bis = champ.get("recommendItems")
        if champ_bis:
            champ_alt = champ.get("name")
            champ_name = champ.get("key").lower()
            champ_src = champ.get("imageUrl")
            if champ_src:
                champ_src = (
                    champ_src
                    if champ_src.startswith("https:")
                    else "https:" + champ_src
                )
            filtered_data["champs"][champ_name] = {
                "alt": champ_alt,
                "bis": champ_bis,
                "src": champ_src,
            }

    filtered_data["items"] = {}
    for item in items:
        item_name = item.get("ingameKey")
        item_src = item.get("imageUrl")
        if item_name and item_src:
            item_src = (
                item_src if item_src.startswith("https:") else "https:" + item_src
            )
            item_comp = item.get("compositions")
            item_alt = item.get("name")
            if item_comp:
                item_alt += " (" + " + ".join(item_comp) + ")"
            filtered_data["items"][item_name] = {"alt": item_alt, "src": item_src}

    team_comps = list()
    for comp in comps:
        slots = comp.get("data", {}).get("slots", {})

        team = list()
        for slot in slots:
            comp_champ = slot.get("champion")
            if comp_champ:
                comp_champ = comp_champ.lower()
                if comp_champ in ["azirultsoldier", "freljordprop", "tibbers"]:
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
