from dotenv import load_dotenv
from logging.config import fileConfig
import logging
import json
import os
import re

from curl_cffi import requests

load_dotenv(os.path.expanduser("~/python/.env"))
fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("gl-ibp")


def clean(data: dict) -> list | None:
    data1 = data.get("props")
    if data1:
        data2 = data1.get("pageProps")
        if data2:
            data3 = data2.get("availableModels")
            if data3:
                return data3
    return None


def save(data) -> None:
    with open(
        file=os.path.expanduser("~/data/ibp.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)
    logger.info("ibp.json saved")


def load(address: str) -> list:
    pattern = re.compile(r"({\"props\"[^<]+)")
    response = requests.get(url=address, impersonate="chrome")
    if response.status_code == 200:
        re_match = pattern.search(response.text)
        if re_match:
            dump = json.loads(re_match.group(1))
            data = clean(dump)
            if data:
                return data
            else:
                logger.warning("data not found")
        else:
            logger.warning("json not found")
    else:
        logger.warning("returned status code %s", response.status_code)
    return []


def main() -> None:
    url = os.getenv("URL_IBP")
    result = load(address=url)
    url = os.getenv("URL_IBPR")
    result += load(address=url)
    if result:
        save(result)


if __name__ == "__main__":
    main()
