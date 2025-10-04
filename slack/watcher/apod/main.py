import logging
from logging.config import fileConfig
import os
import re
from urllib.parse import urljoin

from curl_cffi import requests
from dotenv import load_dotenv
from selectolax.parser import HTMLParser
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient

slagger = logging.getLogger(name="slack_sdk.web.base_client")
slagger.disabled = 1

load_dotenv(dotenv_path=os.path.expanduser("~/python/.env"))
fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger(name="apod--")

# ADDRESS = "https://apod.nasa.gov/apod/astropix.html"
# temporary solution during NASA haitus due to potential goverment shutdown
ADDRESS = "http://www.star.ucl.ac.uk/~apod/apod/ap251003.html"


def clean_explanation(text: str) -> str:
    # replace n tags with spaces
    text = re.sub(pattern=r"\n", repl=" ", string=text, flags=re.I)
    # remove preamble + tags p b i u s
    text = re.sub(
        pattern=r"\<\/?[bipus]\>|\s*explanation:\s*", repl="", string=text, flags=re.I
    )
    # clean spaces
    text = re.sub(pattern=r"\s+", repl=" ", string=text, flags=re.I)
    # replace short links
    text = re.sub(
        pattern=r"(?<=href=\")(ap\d+\.html?)",
        repl=urljoin(ADDRESS, r"\1"),
        string=text,
        flags=re.I,
    )
    # reformat hyperlinks
    text = re.sub(
        pattern=r"\<a\s*href=\"([^\"]+)\"\>([^\<]+)\<\/a\>",
        repl=r"<\1|\2>",
        string=text,
        flags=re.I,
    )

    return text.strip()


def slack_message(
    block: list | None, message="Astronomy Picture of the Day", links=False, media=False
) -> None:
    client = WebClient(token=os.getenv("WATCHER_TOKEN"))
    try:
        client.chat_postMessage(
            channel=os.getenv("APOD_CHANNEL"),
            unfurl_links=links,
            unfurl_media=media,
            blocks=block,
            text=message,
        )
        logger.info("slack message sent")
    except SlackApiError as error:
        logger.error("%s", error)


if __name__ == "__main__":
    response = requests.get(url=ADDRESS, allow_redirects=True)
    if response.status_code == 200:
        tree = HTMLParser(html=response.content)
        title = tree.css_first("b").text().strip()
        image = tree.css_first("img")
        video = tree.css_first("iframe")
        explanation = clean_explanation(text=tree.css_first("body > p").html)

        if image is not None:
            src = urljoin(ADDRESS, image.attrs["src"])
            temp = [
                {"type": "image", "image_url": src, "alt_text": title},
                {
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": explanation}],
                },
            ]

            slack_message(block=temp)

        elif video is not None:
            re_video = re.search(
                pattern=r"(?<=youtube).*?([\-\w]{11})", string=video.attrs["src"]
            )

            if re_video:
                video_url = f"https://www.youtube.com/watch?v={re_video.group(1)}"

            else:
                video_url = video.attrs["src"]

            slack_message(block=None, message=video_url, media=True)

            temp = [
                {
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": explanation}],
                },
            ]

            slack_message(block=temp, message="Astronomy Video of the Day")

        else:
            logger.warning("image/video not found")
            slack_message(
                block=None,
                message="No APOD found because Mika is a stinky poopoo head.\nClick the link yourself you lazy sacks of crap:\nhttps://apod.nasa.gov/apod/",
            )
        if temp:
            logger.info(temp)
    else:
        logger.warning("returned status code %s", response.status_code)
