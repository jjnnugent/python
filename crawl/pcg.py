from logging.config import fileConfig
import logging
import json
import os
import re

from curl_cffi import requests
from dotenv import load_dotenv
from selectolax.parser import HTMLParser

load_dotenv(os.path.expanduser("~/python/.env"))
fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger(name="gl-pcg")


def save_file(data) -> None:
    with open(
        file=os.path.expanduser("~/data/pcg.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)
    logger.info("pcg.json saved")


def main() -> None:
    address = os.getenv("URL_PCG")
    response = requests.get(url=address, allow_redirects=True, impersonate="chrome")
    if response.status_code == 200:
        tree = HTMLParser(html=response.text)
        nodes = tree.css("div.hawk-deal-widget-container")

        data = []
        names = ["brand", "gpu", "cpu", "inch", "res", "hz", "mem", "ssd", "price"]
        for node in nodes:
            parts = node.css_first("p > strong:nth-child(3)").text().split("|")
            if len(parts) != 9:
                continue
            temp = {}
            for key, value in zip(names, parts):
                temp[key] = value.strip()
            if temp.get("gpu") is None or temp.get("cpu") is None:
                continue
            price = (
                node.css_first("p > a > strong").text().replace("\u00a3", "").strip()
            )
            price = (
                re.search(pattern=r"((?:\d+,)?\d+(?:\.\d+)?)", string=price, flags=re.I)
                .group(1)
                .replace(",", "")
            )
            temp["price"] = price
            if temp.get("price") is None:
                continue
            temp["link"] = node.css_first("p > a").attrs["href"]
            temp["brand"] = re.sub(
                pattern=r"\s*(?:Price|watch:|➖|🔽|🔼|NEW|DEAL|!)",
                repl="",
                string=temp["brand"],
                flags=re.I,
            )
            data.append(temp)
        if data:
            save_file(data)
        else:
            logger.warning("data not found")
    else:
        logger.warning("returned with %s", response.status_code)


if __name__ == "__main__":
    main()
