import logging
from logging.config import fileConfig
import json
import os
import re

from curl_cffi import requests
from utils.file import save_json
from utils.slack import SlackHandler


def dict_keys(dump: dict, end: str) -> list:
    keys = ["props", "pageProps", "dehydratedState", "queries", "state", "data", end]
    step = dump
    for key in keys:
        step = step.get(key, {})
        if not step:
            return []

        if key == "queries":
            if end == "champions":
                step = step[0]
            elif end == "items":
                step = step[2]
            else:
                step = step[3]
    return step


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

            champs = dict_keys(dump=json_data, end="champions")
            if not champs:
                logger.warning("missing champs data")
            comps = dict_keys(dump=json_data, end="guideDecks")
            if not comps:
                logger.warning("missing comps data")
            items = dict_keys(dump=json_data, end="items")
            if not items:
                logger.warning("missing items data")
            new = dict()

            for result in champs:
                bis = result.get("recommendItems")
                if bis:
                    name = result.get("key").lower()
                    new[name] = bis

                    for i in range(len(bis)):
                        for item in items:
                            item_alt = item.get("key")
                            item_name = item.get("ingameKey")
                            if item_name and item_name == bis[i]:
                                image_url = item.get("imageUrl")
                                bis[i] = [image_url if image_url.startswith("https:") else "https:" + image_url, item_alt]
                else:
                    continue

            new['comps'] = list()
            for comp in comps:
                party = list()
                name = comp.get("name")
                slots = comp.get("data", {}).get("slots", {})
                if slots:
                    for slot in slots:
                        champion = slot.get("champion").lower()
                        if slot:
                            party.append(champion)
                if party:
                    new['comps'].append([name] + party)

            save_json(data=new, name=os.path.expanduser("~/data/tft.json"))

        else:
            logger.warning("data not found")
    else:
        logger.warning("%s returned", response.status_code)
