from logging.config import fileConfig
import logging
import json
import os
import re

from curl_cffi import requests
from dotenv import load_dotenv
from selectolax.parser import HTMLParser
from slack_sdk import WebClient

fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger(name="gl-pcg")
load_dotenv(os.path.expanduser("~/python/.env"))


def save_file(data) -> None:
    with open(
        file=os.path.expanduser("~/data/pcg.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)
    logger.info("pcg.json saved")


def slack_message(message: str) -> None:
    client = WebClient(token=os.getenv("WATCHER_TOKEN"))
    client.chat_postMessage(channel=os.getenv("SANDBOX_CHANNEL"), text=message)


def main() -> None:
    address = os.getenv("URL_PCG")
    response = requests.get(url=address, allow_redirects=True, impersonate="chrome")

    if response.status_code == 200:
        tree = HTMLParser(response.text)
        nodes = tree.css("div.hawk-deal-widget-main")

        data = []
        for node in nodes:
            link = node.css_first("a.hawk-affiliate-link-container").attrs["href"]
            price = node.css_first("span.hawk-deal-widget-title-price").text()
            price = re.sub(pattern=r"now(\s*)|\$|,", repl="", string=price, flags=re.I)

            if price.startswith("£"):
                continue

            brand = node.css_first("span.hawk-deal-widget-title-product-title").text()
            brand = re.sub(pattern=r"(\s*)\|.*$", repl="", string=brand, flags=re.I)
            props = node.css_first("p > strong").text()
            props = re.sub(
                pattern=r"key\s*specs\:\s*|\s*hz|\-inch",
                repl="",
                string=props,
                flags=re.I,
            )
            props = re.sub(pattern=r"\s*\|\s*$", repl="", string=props, flags=re.I)
            props = props.split(" | ", maxsplit=6)

            if len(props) < 6:
                continue

            temp = {}
            names = ["brand", "price", "link", "gpu", "cpu", "inch", "hz", "mem", "ssd"]
            for key, value in zip(names, [brand, price, link] + props[:3] + props[-3:]):
                temp[key] = value
            data.append(temp)

        if data:
            save_file(data)
        else:
            logger.warning("no data found")
            slack_message(message="[WARNING] PCG no data found")

    else:
        logger.warning("response returned %s", response.status_code)
        slack_message(message=f"[WARNING] PCG returned {response.status_code}")


if __name__ == "__main__":
    main()
