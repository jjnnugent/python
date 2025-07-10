from datetime import datetime
from logging.config import fileConfig
import logging
import json
import os
import re
from time import sleep

from curl_cffi import requests
from dotenv import load_dotenv
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient

slagger = logging.getLogger(name="slack_sdk.web.base_client")
slagger.disabled = 1

load_dotenv(os.path.expanduser("~/python/.env"))
fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("wlist-")

RE_VIDEOS = re.compile(
    pattern=r"(?:reelWatchEndpoint|(?:playlist)?[vV]ideoRenderer)\":\{\"videoId\":\"([^\"]+)\""
)


def load_data() -> dict:
    with open(
        file=os.path.expanduser("~/data/watchlist.json"), mode="r", encoding="utf-8"
    ) as file:
        return json.load(fp=file)


def save_data(data: dict) -> None:
    with open(
        file=os.path.expanduser("~/data/watchlist.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)
    logger.info("watchlist.json saved")


def load_videos(name: str, channel_type: str) -> list:
    sleep(2)
    if channel_type == "shorts":
        address = f"https://www.youtube.com/@{name}/shorts"
    elif channel_type == "playlist" or channel_type == "playlist_bottom":
        address = f"https://www.youtube.com/playlist?list={name}"
    else:
        address = f"https://www.youtube.com/@{name}/videos"
    response = requests.get(url=address)
    if response.status_code == 200:
        video_ids = RE_VIDEOS.findall(string=response.text)
        if channel_type == "playlist_bottom":
            latest = video_ids[-3:]
            latest.reverse()
            return latest
        return video_ids[:3]
    else:
        logger.warning("%s returned status code %s", address, response.status_code)
        return []


def slack_message(channel_id: str, block: list | None, message: str | None) -> bool:
    client = WebClient(token=os.getenv("WATCHER_TOKEN"))
    try:
        client.chat_postMessage(
            channel=channel_id, text=message, blocks=block, unfurl_media=True
        )
        return True
    except SlackApiError as error:
        logger.error(error)
    return False


if __name__ == "__main__":
    modified = False
    now = datetime.now()
    day = (
        now.isoweekday()
    )  # 1 = Mon, 2 = Tue, 3 = Wed, 4 = Thu, 5 = Fri, 6 = Sat, 7 = Sun
    hour = now.hour

    data = load_data()
    for format, entry in data.items():
        for channel in entry:
            channel_days = data[format][channel].get("days_of_week")
            channel_hour = data[format][channel].get("hour_of_day")
            slack_channel = data[format][channel].get("slack_channel")
            title = channel
            if data[format][channel].get("title") is not None:
                title = data[format][channel].get("title")

            # format = data[channel].get("type")
            old = data[format][channel].get("videos")

            if len(old) == 0:
                logger.info("%s loading first videos", title)
                data[format][channel]["videos"] = load_videos(
                    name=channel, channel_type=format
                )
                data[format][channel]["last_updated"] = str(now)
                modified = True
                continue

            if channel_days is None or day in channel_days:
                if channel_hour is None or channel_hour == hour:
                    new = load_videos(name=channel, channel_type=format)
                    if old == new:
                        logger.debug("%s no change %s", title, old)
                    else:
                        link = "https://www.youtube.com/"
                        link += "shorts/" if format == "shorts" else "watch?v="
                        link += new[0]
                        slack_block = [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f"{title} new video!\n{link}",
                                },
                            }
                        ]

                        logger.info("%s new video %s", title, new)
                        sent = slack_message(
                            channel_id=slack_channel,
                            block=slack_block,
                            message=f"{title} new video!",
                        )

                        if sent:
                            data[format][channel]["videos"] = new
                            data[format][channel]["last_updated"] = str(now)
                            modified = True

                else:
                    logger.debug("%s not hour of %s", title, channel_hour)
            else:
                logger.debug("%s not day of %s", title, channel_days)

    if modified:
        save_data(data)
    else:
        logger.debug("no updates")
