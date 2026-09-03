import datetime
import logging
import json
import os
import re

from random import randint
from time import sleep

from curl_cffi import requests
from dotenv import load_dotenv
from utils.file import load_json
from utils.file import save_json
from utils.slack import SlackHandler
from utils.slack import slack_message


logging.config.fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("watchl")
logger.addHandler(SlackHandler())
load_dotenv(os.path.expanduser("~/python/.env"))
RE_VIDEOS = re.compile(r"ytInitialData\s*=\s*({.*?)(?=<\/)")
BOT_TOKEN = os.getenv("WATCHER_TOKEN")


def load_videos(channel_type: str, channel_name: str) -> list:
    n = randint(2, 8)
    sleep(n)
    result = []
    address = "https://www.youtube.com/@" + channel_name
    if channel_type == "shorts":
        address += "/shorts"
    else:
        address += "/videos"

    try:
        response = requests.get(
            url=address,
            allow_redirects=True,
            impersonate="chrome")
    except Exception as e:
        logger.error(e)
        return []

    if response.status_code == 200:
        try:
            re_match = RE_VIDEOS.search(response.text)
            if re_match:
                dump = json.loads(re_match.group(1))
            else:
                logger.error("%s regex not found", channel_name)
                return []

            count = 0
            if channel_type == "shorts":
                tabs = dump['contents']['twoColumnBrowseResultsRenderer']['tabs']
                for tab in tabs:
                    if tab['tabRenderer'].get("title") == "Shorts":
                        data = tab['tabRenderer']['content']['richGridRenderer']['contents']
                        break

                for item in data:
                    if item.get("continuationItemRenderer"):
                        break

                    else:
                        count += 1
                        title = item['richItemRenderer']['content']['shortsLockupViewModel']['overlayMetadata']['primaryText']['content']
                        views = item['richItemRenderer']['content']['shortsLockupViewModel']['overlayMetadata']['secondaryText']['content']
                        video_id = item['richItemRenderer']['content']['shortsLockupViewModel'][
                            'onTap']['innertubeCommand']['reelWatchEndpoint']['videoId']
                        result.append(
                            {
                                'title': title,
                                'views': views,
                                'video_id': video_id,
                            }
                        )

                    if count == 3:
                        break
            else:
                tabs = dump['contents']['twoColumnBrowseResultsRenderer']['tabs']
                for tab in tabs:
                    if tab['tabRenderer'].get("title") == "Videos":
                        data = tab['tabRenderer']['content']['richGridRenderer']['contents']
                        break

                for item in data:
                    keep_going = True
                    if item.get("continuationItemRenderer"):
                        break

                    else:
                        meta_rows = item['richItemRenderer']['content']['lockupViewModel']['metadata'][
                            'lockupMetadataViewModel']['metadata']['contentMetadataViewModel']['metadataRows']

                        for meta_item in meta_rows:
                            if meta_item.get("badges"):
                                keep_going = False

                        if keep_going:
                            count += 1
                            title = item['richItemRenderer']['content']['lockupViewModel']['metadata'][
                                'lockupMetadataViewModel']['title']['content']
                            views = meta_rows[-1]['metadataParts'][0]['text']['content']
                            when = meta_rows[-1]['metadataParts'][1]['text']['content']
                            video_id = item['richItemRenderer']['content']['lockupViewModel']['contentId']
                            result.append(
                                {
                                    'title': title,
                                    'views': views,
                                    'when': when,
                                    'video_id': video_id,
                                }
                            )

                        else:
                            continue

                    if count == 3:
                        break

        except Exception as e:
            logger.error(e)
            return []

    else:
        logger.warning("%s %s", channel_name, response.status_code)

    return result


if __name__ == "__main__":
    # 1 = Mon, 2 = Tue, 3 = Wed, 4 = Thu, 5 = Fri, 6 = Sat, 7 = Sun
    current_time = datetime.datetime.now()
    today = current_time.isoweekday()
    hour = current_time.hour
    modified = False

    data = load_json(name=os.path.expanduser("~/data/watchlist.json"))
    for video_type, entry in data.items():
        for channel in entry:
            channel_days = data[video_type][channel].get("days_of_week")
            channel_hours = data[video_type][channel].get("hour_of_day")
            channel_id = data[video_type][channel].get("slack_channel")
            old = data[video_type][channel].get("videos")

            if len(old) == 0:
                new = load_videos(channel_type=video_type,
                                  channel_name=channel)
                if new:
                    data[video_type][channel]['videos'] = new
                    data[video_type][channel]['last_updated'] = str(
                        current_time)
                    modified = True
                    logger.info("%s first videos loaded %s", channel, new)
                else:
                    logger.warning("%s first videos not found", channel)

            elif today in channel_days and hour in channel_hours:
                new = load_videos(channel_type=video_type,
                                  channel_name=channel)
                old_id = old[0]['video_id']
                new_id = new[0]['video_id']
                # print(f"old id = {old_id} -- new id = {new_id}")
                if old_id == new_id:
                    logger.debug("%s no update", channel)

                elif new_id:
                    update_slack = False
                    data[video_type][channel]['videos'] = new
                    data[video_type][channel]['last_updated'] = str(
                        current_time)
                    modified = True
                    logger.info("%s new %s", channel, new)

                    keywords = data[video_type][channel].get("keywords")
                    title = new[0]['title']
                    if keywords:
                        re_match = re.search(
                            pattern=keywords, string=title, flags=re.I)
                        if re_match:
                            update_slack = True
                    else:
                        update_slack = True

                    if update_slack:
                        views = new[0]['views']
                        views = views if views.endswith(
                            "views") else views + " views"
                        href = "https://www.youtube.com/"
                        if video_type == "shorts":
                            href += "shorts/"
                        else:
                            href += "watch?v="
                        href += new[0].get("video_id")
                        block = [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f"{href}"
                                }
                            }
                        ]
                        sent = slack_message(
                            passw=BOT_TOKEN,
                            # channel=os.getenv("SANDBOX_CHANNEL"),
                            channel=channel_id,
                            blocks=block,
                            text=f"@{channel} {title} ({views})",
                        )
                else:
                    logger.warning("%s videos not found", channel)

            else:
                logger.debug("not %s days %s or hours %s",
                             channel, channel_days, channel_hours)

    if modified:
        save_json(data=data, name=os.path.expanduser("~/data/watchlist.json"))
    else:
        logger.info("no updates")
