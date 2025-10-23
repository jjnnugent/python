from logging.config import fileConfig
from json.decoder import JSONDecodeError
import logging
import json
import os
import re

from curl_cffi import requests
from dotenv import load_dotenv
from tools import save_json

load_dotenv()
fileConfig(os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("crawl-")


# mark


def clean(data: dict) -> list | None:
    data1 = data.get("props")
    if data1:
        data2 = data1.get("pageProps")
        if data2:
            data3 = data2.get("availableModels")
            if data3:
                return data3
    return None


# gld
def gld() -> None:
    result = ""
    response = requests.get(
        url=os.getenv("URL_GLD"),
        impersonate="chrome",
    )
    if response.status_code == 200:
        try:
            result = response.json()
        except JSONDecodeError as e:
            logger.error(e)
        if result:
            filename = "gld.json"
            save_json(data=result, name=filename)
            logger.info("%s saved", filename)
    else:
        logger.warning("returned status code %s", response.status_code)


# ibp
def ibp() -> None:
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


# pcg

# thw


def main() -> None:
    print("Hello")


if __name__ == "__main__":
    main()
