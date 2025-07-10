from logging.config import fileConfig
import logging
import json
import os
import re

from curl_cffi import requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/python/.env"))
fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("gl-bgl")


def main() -> None:
    address = os.getenv("URL_BGL")
    response = requests.get(url=address, impersonate="chrome")
    if response.status_code == 200:
        pattern = re.compile(r"result\\\":({.*}),\\\"unique")
        re_match = pattern.search(string=response.text)
        if re_match:
            dump = re_match.group(1)
            dump = re.sub(pattern=r"\\\\\\\"", repl="", string=dump, flags=re.I)
            dump = re.sub(pattern=r"\\", repl="", string=dump, flags=re.I)
            json_dump = json.loads(dump)
            save_data(json_dump)
        else:
            logger.warning("no re match found")
    else:
        logger.warning("returned status code %s", response.status_code)


def save_data(data) -> None:
    with open(
        file=os.path.expanduser("~/data/bgl.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)
    logger.info("bgl.json saved")


if __name__ == "__main__":
    main()
