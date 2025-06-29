from logging.config import fileConfig
import logging
import json
import os

from curl_cffi import requests
from selectolax.parser import HTMLParser

fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger(name="gl-pcg")


def load() -> None:
    address = os.getenv("URL_PCG")
    response = requests.get(url=address)
    if response.status_code == 200:
        tree = HTMLParser(response.text)
        nodes = tree.css('div[data-editorial-currency="USD"]')

        data = []
        items = ["brand", "gpu", "cpu", "inch", "res", "hz", "mem", "ssd", "price"]
        for node in nodes:
            parts = node.attrs["data-widget-introduction"].split("|")
            if len(parts) != 9:
                continue
            temp = {}
            for key, value in zip(items, parts):
                temp[key] = value.strip()
            data.append(temp)
        if data:
            save(data)
            logger.info("pcg.json saved")
        else:
            logger.warning("data not found")
    else:
        logger.warning("returned status code %s", response.status_code)


def save(data) -> None:
    with open(
        file=os.path.expanduser("~/data/pcg.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)


def main() -> None:
    load()


if __name__ == "__main__":
    main()
