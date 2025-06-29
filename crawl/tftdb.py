import logging
import logging.config

from dotenv import load_dotenv
from curl_cffi import requests
import json
import os

logging.config.fileConfig(os.path.expanduser(("~/logs/logging.conf")))
logger = logging.getLogger("tftdb-")

load_dotenv(os.path.expanduser("~/python/.env"))


def save(data) -> None:
    with open(
        file=os.path.expanduser("~/data/tft.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)
        logger.info("file saved")


def clean(source) -> dict:
    logger.info("cleaning data...")

    data = dict()
    for k, v in source["units"].items():
        data[k.lower()[6:]] = [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "image",
                        "image_url": "https://ddragon.leagueoflegends.com/cdn/14.23.1/img/tft-item/"
                        + item["itemName"]
                        + ".png",
                        "alt_text": item["itemName"],
                    }
                    for item in v["items"]
                ][:5],
            }
        ]

    logger.info("data cleaned")
    return data


def load() -> list | dict:
    logger.info("retrieving data...")
    response = requests.get(url=os.getenv("URL_TF"), impersonate="chrome")
    if response.status_code == 200:
        logger.info("returned status code %s", response.status_code)
        return response.json()
    else:
        logger.warning("returned status code %s", response.status_code)
        exit(response.status_code)
    return list()


def main() -> None:
    logger.info("now running...")
    data = load()
    data = clean(source=data)
    save(data)
    logger.info("completed")


if __name__ == "__main__":
    main()
