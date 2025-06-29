from dotenv import load_dotenv
from logging.config import fileConfig
import logging
import json
import os
import re

from curl_cffi import requests
from selectolax.parser import HTMLParser

load_dotenv(os.path.expanduser("~/python/.env"))
fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("thw---")


def load_data() -> None:
    response = requests.get(
        url=os.getenv("URL_THW"),
        impersonate="chrome",
    )
    data = []
    if response.status_code == 200:
        nodes = HTMLParser(html=response.text).css("div.hawk-deal-widget-responsive")
        for node in nodes:
            temp = {}
            href = node.css_first("a").attrs["href"]
            temp["link"] = href
            text = node.text(strip=True)
            # brand
            re_match = re_brand.search(string=text)
            if re_match:
                temp["brand"] = re_match.group(1).strip()
            # price
            re_match = re_price.search(string=text)
            if re_match:
                temp["cost"] = float(re_match.group(1).replace(",", "").strip())
            # cpu
            re_match = re_cpu.search(string=text)
            if re_match:
                cpu = re_match.group(1)
                if cpu.startswith("Ryzen"):
                    cpu = "AMD " + cpu
                    cpu = cpu.replace("-", " ")
                else:
                    cpu = "Intel Core " + cpu
                temp["cpu"] = cpu
            # gpu
            re_match = re_gpu.search(string=text)
            if re_match:
                temp["gpu"] = "GeForce RTX " + re_match.group(1).strip() + " Laptop GPU"
            data.append(temp)
        save_data(data)

    else:
        logger.warning("returned status code %s", response.status_code)


def save_data(data) -> None:
    with open(
        file=os.path.expanduser("~/data/thw.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)
    logger.info("thw.json saved")


re_brand = re.compile(r"([^:\(\n]+)", flags=re.I)
re_price = re.compile(r"now \$([\d,\.]+)")
re_cpu = re.compile(r"((?:Ryzen\s*|i)\d(?:-|\s*)[\w]+\b)")
re_gpu = re.compile(r"(?<=RTX)\s*(\d{4}(?:\s*Ti)?)", flags=re.I)


def main() -> None:
    load_data()


if __name__ == "__main__":
    main()
