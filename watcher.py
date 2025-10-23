from datetime import datetime
import logging
import json
import os
import re

from curl_cffi import requests
from dotenv import load_dotenv
from slack_bolt import App

logging.basicConfig(level=logging.DEBUG)

RE_CHANNEL = re.compile(
    r"^https://(?:www\.)?youtube\.com/(?:@|playlist\?list=)([^/\&]+)"
)


def verify(address: str) -> bool:
    response = requests.get(url=address)
    if response.status_code == 200:
        return True
    return False


def load_data() -> None:
    with open(
        file=os.path.expanduser("~/data/watchlist.json"), mode="r", encoding="utf-8"
    ) as file:
        return json.load(fp=file)


def save_data(data) -> None:
    with open(
        file=os.path.expanduser("~/data/watchlist.json"), mode="w", encoding="utf-8"
    ) as file:
        json.dump(obj=data, fp=file, indent=2)


def help(slash: str) -> str:
    return f""


load_dotenv(os.path.expanduser("~/python/.env"))
the_watcher = App(
    signing_secret=os.getenv("WATCHER_SS"), token=os.getenv("WATCHER_TOKEN")
)


@the_watcher.command("/watch")
def command_watch(ack, command, respond) -> None:
    ack()
    print(command)
    text = command["text"]

    re_match = RE_CHANNEL.search(string=text)
    if not re_match:
        respond("Link not found.")

    else:
        channel = re_match.group(1)
        valid = verify(address=text)
        if not valid:
            respond(f"{channel} does not exist in this reality.")

        else:
            data = load_data()
            if text.endswith("/shorts"):
                format = "shorts"

            elif channel.startswith("PL"):
                format = "playlist"

            else:
                format = "default"

            if channel in data[format].keys():
                respond(f"{channel} is already part of my cosmic observations.")

            else:
                now = datetime.now()
                day = now.isoweekday()
                hour = now.hour
                data[format][channel] = {
                    "days_of_week": [day],
                    "hour_of_day": hour,
                    "last_updated": None,
                    "slack_channel": command["channel_id"],
                    "type": format,
                    "videos": [],
                }

                save_data(data=data)

                user = command["user_name"]
                respond(response_type="in_channel", text=f"{user}, {channel} shall be watched.")


if __name__ == "__main__":
    the_watcher.start(port=52258)
