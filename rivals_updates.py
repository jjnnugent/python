import asyncio
import json
import logging
import os
import re
from logging.config import fileConfig

from aiohttp import ClientSession
from curl_cffi import requests
from discord import Webhook
from dotenv import load_dotenv
from selectolax.lexbor import LexborHTMLParser

from utils.file import load_json, save_json
from utils.slack import SlackHandler

load_dotenv(os.path.expanduser("~/python/.env"))
fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("rivals")
logger.addHandler(SlackHandler())

file_path = os.path.expanduser("~/data/rivals_updates.json")
json_data = load_json(name=file_path)
webhook_url = os.getenv("DISCORD_JEFF")


async def discord_message(text: str) -> None:
    async with ClientSession() as s:
        webhook = Webhook.from_url(url=webhook_url, session=s)
        await webhook.send(content=text)
        logger.info("%s sent", text)


def get_tabs(dump: dict) -> list | None:
    return dump["contents"]["twoColumnBrowseResultsRenderer"].get("tabs")


def get_contents(dump: dict) -> list | None:
    return dump["tabRenderer"]["content"]["richGridRenderer"].get("contents")


def check_pn() -> None:
    address = "https://marvelrivals.gg/news/patch-notes/"
    response = requests.get(url=address, impersonate="chrome")
    tree = LexborHTMLParser(response.text)
    nodes = tree.css('div.entries a[rel="bookmark"]')

    new_links = []
    for node in nodes[:4]:
        new_links.append(node.attrs["href"])

    old_links = json_data.get("pn")

    if old_links == new_links:
        logger.info("no pn change")

    else:
        asyncio.run(discord_message(new_links[0]))
        json_data["pn"] = new_links
        save_json(data=json_data, name=os.path.expanduser(file_path))


def check_yt() -> None:
    address = "https://www.youtube.com/@MarvelRivals/videos"
    response = requests.get(url=address, impersonate="chrome")
    re_match = re.search(
        pattern=r"({\"responseContext\".*?);?<\/",
        string=response.text,
        flags=re.IGNORECASE,
    )

    if re_match:
        json_re = json.loads(re_match.group(1))
        tabs = get_tabs(dump=json_re)

        for tab in tabs:
            if tab.get("tabRenderer", {}).get("title", {}) == "Videos":
                contents = get_contents(dump=tab)
                break

        old_ids = json_data.get("yt")
        new_ids = []
        for content in contents[:4]:
            if content.get("continuationItemRenderer"):
                break

            title = content["richItemRenderer"]["content"]["lockupViewModel"][
                "metadata"
            ]["lockupMetadataViewModel"]["title"].get("content")

            if re.search(pattern=r"Reveal|Trailer", string=title, flags=re.IGNORECASE):
                video_id = content["richItemRenderer"]["content"][
                    "lockupViewModel"
                ].get("contentId")
                new_ids.append([title, video_id])

            else:
                continue

        if old_ids == new_ids:
            logger.info("no yt change")

        else:
            video_link = f"https://youtube.com/watch?v={new_ids[0][1]}"
            asyncio.run(discord_message(video_link))
            json_data["yt"] = new_ids
            save_json(data=json_data, name=file_path)

    else:
        logger.warning("no json data match found")


if __name__ == "__main__":
    check_pn()
    check_yt()
