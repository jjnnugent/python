from logging.config import fileConfig
import logging
import os
import re
from time import sleep
from urllib.parse import urljoin

from curl_cffi import requests
from dotenv import load_dotenv
from selectolax.parser import HTMLParser

from utils.slack import slack_message


load_dotenv()
BOT = os.getenv("WATCHER_TOKEN")
CHANNEL = os.getenv("APOD_CHANNEL")
ICON = "https://ik.imagekit.io/eetmbg795/ngt1-br.png"
USERNAME = "Neil deGod Tyson"


def main() -> None:
    # image
    # address = "https://apod.nasa.gov/apod/ap250919.html"

    # video/mp4
    # address = "https://apod.nasa.gov/apod/ap250518.html"

    # youtube
    # address = "https://apod.nasa.gov/apod/ap250506.html"

    # mirror
    # address = "http://sprite.phys.ncku.edu.tw/astrolab/mirrors/apod_e/apod.html"

    address = "https://apod.nasa.gov/apod/astropix.html"
    response = requests.get(url=address)
    tree = HTMLParser(html=response.text)

    frame = tree.css_first("iframe")
    image = tree.css_first("img")
    name = tree.css_first("b")
    source = tree.css_first("source")
    if name:
        name = name.text(strip=True)

    desc = tree.css_first("body > p")
    if desc:
        desc_html = desc.html
        desc = desc.text()
        desc = re.sub(pattern=r"\s+", repl=" ", string=desc)
        desc = re.sub(pattern=r"\s*explanation:\s*", repl="", string=desc, flags=re.I)
        if image:
            src = urljoin(base=address, url=image.attrs["src"])
            ext = os.path.splitext(src)[-1]
            download = requests.get(url=src).content
            file_path = os.path.expanduser("~/data/") + "apod" + ext
            with open(file=file_path, mode="wb") as file:
                file.write(download)

            slack_message(
                passw=BOT,
                upload=True,
                channel=CHANNEL,
                file=file_path,
                title=name,
                alt_txt=desc,
            )

        elif frame or source:
            if frame:
                media = "https://www.youtube.com/watch?v=" + re.search(
                    pattern=r"(?<=youtube).*?([\w\-]{11})", string=frame.attrs["src"]
                ).group(1)
            else:
                media = urljoin(base=address, url=source.attrs["src"])

            # extend links
            desc_html = re.sub(
                pattern=r"(ap\d+?\.html?)",
                repl=urljoin(base=address, url=r"\1"),
                string=desc_html,
                flags=re.I,
            )

            # format links for slack
            desc_html = re.sub(
                pattern=r"<\s*a.*?(?<=href)=\"([^\"]+)[^>]+>([^<]+)<\s*/\s*a\s*>",
                repl=r"<\1|\2>",
                string=desc_html,
                flags=re.I,
            )

            # clean html
            desc_html = re.sub(
                pattern=r"<\/?[bipus]>|\s*explanation:\s*",
                repl="",
                string=desc_html,
                flags=re.I,
            )

            # format lines and spaces
            desc_html = re.sub(
                pattern=r"\s+|\n", repl=" ", string=desc_html, flags=re.I
            )
            desc_html = desc_html.strip()

            block = [
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": desc if frame else desc_html}
                    ],
                },
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": media}],
                },
            ]

            sent = slack_message(
                passw=BOT,
                timing=True,
                channel=CHANNEL,
                text=name,
                blocks=block,
                unfurl_links=False,
                unfurl_media=True,
                icon_url=ICON,
                username=USERNAME,
            )

            if frame:
                sleep(5)

                block = [
                    {
                        "type": "context",
                        "elements": [{"type": "mrkdwn", "text": desc_html}],
                    },
                    {"type": "divider"},
                    {
                        "type": "context",
                        "elements": [{"type": "mrkdwn", "text": media}],
                    },
                ]

                slack_message(
                    passw=BOT,
                    update=True,
                    channel=CHANNEL,
                    ts=sent,
                    blocks=block,
                    text=name,
                )

    else:
        slack_message(
            passw=BOT,
            channel=CHANNEL,
            text=f"APOD not found\n{address}",
            icon_url=ICON,
            username=USERNAME,
        )

        fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
        logger = logging.getLogger("apod--")
        logger.warning("no image/video found")


if __name__ == "__main__":
    main()
