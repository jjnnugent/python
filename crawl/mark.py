import logging
import logging.config
import json
import os

from curl_cffi import requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/python/.env"))
logging.config.fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("mark--")

URL_CM = os.getenv("URL_CM")
URL_CD = os.getenv("URL_CD")
URL_GM = os.getenv("URL_GM")
URL_GD = os.getenv("URL_GD")
COOK = os.getenv("COOK")


def save(filename: str, data: dict) -> None:
    full = os.path.expanduser("~/data/") + filename
    with open(file=full, mode="w", encoding="utf-8") as file:
        json.dump(obj=data, fp=file, indent=2)
    logger.info("%s saved", filename)


def get_cooks(address: str) -> str:
    response = requests.get(url=URL_CM)
    if response.status_code == 200:
        result = response.cookies.get(COOK)
        logger.info("%s retrieved", result)
    else:
        logger.warning("returned status code %s", response.status_code)
        exit(response.status_code)
    return result


def load(address: str, pw: str, ref: str) -> dict:
    data = dict()
    pw = COOK + "=" + pw
    heads = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9",
        "cookie": pw,
        "priority": "u=1, i",
        "referer": ref,
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "x-requested-with": "XMLHttpRequest",
    }

    response = requests.get(url=address, headers=heads)
    if response.status_code == 200:
        logger.info("returned status code %s", response.status_code)
        data = response.json()
    else:
        logger.warning("returned status code %s", response.status_code)
        exit(response.status_code)
    return data


def main() -> None:
    passw = get_cooks(address=URL_CM)
    cdata = load(address=URL_CD, pw=passw, ref=URL_CM)
    if cdata.get("data") is not None and len(cdata.get("data")) > 0:
        save(filename="cdata.json", data=cdata)
    else:
        logger.warning("cdata None or empty")

    passw = get_cooks(address=URL_GM)
    gdata = load(address=URL_GD, pw=passw, ref=URL_GM)
    if gdata.get("data") is not None and len(gdata.get("data")) > 0:
        save(filename="gdata.json", data=gdata)
    else:
        logger.warning("gdata None or empty")


if __name__ == "__main__":
    main()
