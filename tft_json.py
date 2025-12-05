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
            else:
                step = step[2]
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
            items = dict_keys(dump=json_data, end="items")
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
                                bis[i] = ["http:" + item.get("imageUrl"), item_alt]
                else:
                    continue

            save_json(data=new, name=os.path.expanduser("~/data/tft.json"))

        else:
            logger.warning("data not found")
    else:
        logger.warning("%s returned", response.status_code)
