import json
import logging
import os
import re

from logging.config import fileConfig
from urllib.request import urlopen

from dotenv import load_dotenv
from selectolax.parser import HTMLParser
from utils.slack import SlackHandler
from utils.slack import slack_message


fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("apoday")
logger.addHandler(SlackHandler())

load_dotenv(os.path.expanduser("~/python/.env"))
BOT = os.getenv("WATCHER_TOKEN")
CHANNEL = os.getenv("APOD_CHANNEL")
# CHANNEL = os.getenv("SANDBOX_CHANNEL")

# address = "https://apod.nasa.gov/apod/ap250919.html"  # image
# address = "https://apod.nasa.gov/apod/ap260913.html"  # video/mp4
# address = "https://apod.nasa.gov/apod/ap250506.html"  # youtube

try:
    address = "https://science.nasa.gov/wp-json/wp/v2/apod-basic?per_page=1"
    with urlopen(url=address) as response:
        json_bytes = response.read()

except Exception as err:
    logger.error(err)

json_data = json.loads(json_bytes)[0]
desc_data = json_data.get("explanation")
html_data = json_data.get("basic_html")
titl_data = json_data.get("title")

tree = HTMLParser(html=html_data)
node = tree.css_first("img") or tree.css_first(
    "source") or tree.css_first("iframe")

if not node:
    logger.warning("node not found")

file_url = node.attrs['src']
if re.search(pattern=r"www\.youtube\.com", string=file_url, flags=re.I):
    video_id = re.search(
        pattern=r"(?<=\/)([\w\-]{11})", string=file_url, flags=re.I)
    if video_id:
        yt_url = "https://www.youtube.com/watch?v=" + video_id.group(1)
        slack_block = [
            {
                "type": "section",
                "text": {
                        "type": "mrkdwn",
                        "text": yt_url,
                }
            }
        ]
        slack_message(
            passw=BOT,
            channel=CHANNEL,
            blocks=slack_block,
            text="Astronomy Video of the Day",
        )
    else:
        logger.warning("video id not found")

else:
    file_ext = os.path.splitext(file_url)
    file_name = "apod" + file_ext[-1]

    with urlopen(url=file_url) as response:
        download = response.read()

    with open(file=os.path.expanduser("~/data/" + file_name), mode="wb") as f:
        f.write(download)

    tree_desc = HTMLParser(html=desc_data)
    desc = tree_desc.text()
    desc = re.sub(pattern=r"Explanation:?\s*|APOD's main NASA site.*",
                  repl="", string=desc, flags=re.I)
    desc = re.sub(pattern=r"\s{2,}", repl=" ", string=desc, flags=re.I)

    slack_message(
        passw=BOT,
        upload=True,
        file=os.path.expanduser("~/data/" + file_name),
        title=titl_data,
        alt_txt=desc,
        channel=CHANNEL,
    )
