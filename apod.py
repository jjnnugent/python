from logging.config import fileConfig
import logging
import os
import re
from time import sleep
import urllib.parse

from curl_cffi import requests
from dotenv import load_dotenv
from selectolax.parser import HTMLParser

from utils.slack import slack_message


load_dotenv()
BOT = os.getenv("WATCHER_TOKEN")
CHANNEL = os.getenv("APOD_CHANNEL")
ICON = "https://ik.imagekit.io/eetmbg795/ngt1-br.png"


def main() -> None:
    # image
    # address = "http://sprite.phys.ncku.edu.tw/astrolab/mirrors/apod_e/ap250919.html"

    # video/mp4
    # address = "http://sprite.phys.ncku.edu.tw/astrolab/mirrors/apod_e/ap250518.html"

    # youtube
    # address = "http://sprite.phys.ncku.edu.tw/astrolab/mirrors/apod_e/ap250506.html"


    # ADDRESS = "https://apod.nasa.gov/apod/astropix.html"
    # temporary solution during NASA haitus due to potential goverment shutdown
    address = "http://sprite.phys.ncku.edu.tw/astrolab/mirrors/apod_e/apod.html"
    response = requests.get(url=address)
    tree = HTMLParser(html=response.text)

    desc = tree.css_first("body > p")
    if desc:
        desc = desc.text()
        desc = re.sub(pattern=r"\s+", repl=" ", string=desc)
        desc = re.sub(pattern=r"\s*explanation:\s*", repl="", string=desc, flags=re.I)

    frame = tree.css_first("iframe")
    image = tree.css_first("img")
    name = tree.css_first("b")
    if name:
        name = name.text(strip=True)
    source = tree.css_first("source")

    if image:
        src = urllib.parse.urljoin(base=address, url=image.attrs["src"])

        apod = slack_message(
            passw=BOT,
            timing=True,
            channel=CHANNEL,
            text=f"{name}\n{src}",
            unfurl_links=False,
            unfurl_media=True,
            icon_url=ICON,
            username="Astronomy Picture of the Day",
        )

        sleep(5)

        slack_message(
            passw=BOT,
            update=True,
            channel=CHANNEL,
            ts=apod,
            text=desc,
        )

    elif frame:
        media = frame.attrs["src"]
        media = re.sub(
            pattern=r"^http.*?([\w\-]{11}).*$",
            repl=r"https://www.youtube.com/watch?v=\1",
            string=media,
            flags=re.I,
        )

        slack_message(
            passw=BOT,
            channel=CHANNEL,
            text=f"{desc}\n{media}",
            icon_url=ICON,
            username="Astronomy Video of the Day",
            unfurl_links=False,
            unfurl_media=True,
        )

    elif source:
        src = urllib.parse.urljoin(base=address, url=source.attrs["src"])

        slack_message(
            passw=BOT,
            channel=CHANNEL,
            text=f"{desc}\n{src}",
            icon_url=ICON,
            username="Astronomy Video of the Day",
            unfurl_media=True,
        )

    else:
        slack_message(
            passw=BOT,
            channel=CHANNEL,
            text=f"APOD not found\n{address}",
            icon_url=ICON,
            username="Astronomy Picture of the Day",
            unfurl_links=False,
        )

        fileConfig(os.path.expanduser("~/logs/logging.conf"))
        logger = logging.getLogger("apod--")
        logger.warning("no image/video found")


if __name__ == "__main__":
    main()
