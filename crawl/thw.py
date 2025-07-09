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
logger = logging.getLogger("gl-thw")

def extract_text(text: str, pattern: re.Pattern) -> str | None:
    re_match = pattern.search(text)
    if re_match:
        return re_match.group(1)
    return None

def save_file(data) -> None:
    with open(os.path.expanduser("~/data/thw.json"), mode="w", encoding="utf-8") as file:
        json.dump(obj=data, fp=file, indent=2)
    logger.info("thw.json saved")

def main() -> None:
    address = os.getenv("URL_THW")
    response = requests.get(url=address, allow_redirects=True, impersonate="chrome")
    if response.status_code == 200:
        tree = HTMLParser(html=response.text)
        nodes = tree.css("div.hawk-deal-widget-container")

        pattern_cpu = re.compile(r"((?:Core|Ryzen|Ultra)?\s*i?[3579][-\s]\d{3,}[a-zA-Z]+)")
        pattern_gpu = re.compile(r"(RTX\s*\d{4}(?:\s*Ti)?)")
        pattern_mem = re.compile(r"(\d+GB)\s*of\s*(?:(?:LP)?DDR|RAM|\d+MHz)")
        pattern_price = re.compile(r"(?<=now)\s*\$((?:\d+,)?\d+)")
        pattern_ssd = re.compile(r"(\d+[GT]B)(?=\s*NVMe|\s*PCIe|\s*SSD)")

        data = []
        for node in nodes:
            temp = {}
            html = node.html
            temp['brand'] = node.css_first("img").attrs['alt']
            temp['link'] = node.css_first("a.hawk-affiliate-link-deal-button").attrs['href']
            temp['cpu'] = extract_text(text=html, pattern=pattern_cpu)
            temp['gpu'] = extract_text(text=html, pattern=pattern_gpu)
            temp['mem'] = extract_text(text=html, pattern=pattern_mem)
            temp['price'] = extract_text(text=html, pattern=pattern_price)
            if temp['price'] is not None:
                temp['price'] = temp['price'].replace(",", "")
            temp['ssd'] = extract_text(text=html, pattern=pattern_ssd)
            data.append(temp)
        save_file(data)
    else:
        logger.warning("responded with %s", response.status_code)

if __name__ == "__main__":
    main()
