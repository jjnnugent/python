import os
import re

from curl_cffi import requests
from dotenv import load_dotenv
from logging.config import fileConfig, logging
from selectolax.lexbor import LexborHTMLParser
from slack_sdk import WebClient
from slack_sdk.models import blocks


fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("apod--")

load_dotenv(os.path.expanduser("~/python/.env"))
BOT = os.getenv("WATCHER_TOKEN")
CHANNEL = os.getenv("APOD_CHANNEL")
client = WebClient(token=BOT)
slagger = logging.getLogger(name="slack_sdk.web.base_client")
slagger.disabled = 1

# address = "https://science.nasa.gov/image-article/apod-2026-october-6-a-complete-auroral-oval-from-smile/"  # gif
# address = "https://science.nasa.gov/image-article/apod-2026-october-5-m104-the-sombrero-galaxys-tidal-streams/"  # image
# address = "https://science.nasa.gov/image-article/apod-2026-august-31-launch-of-the-roman-space-telescope/"  # video
# address = "https://science.nasa.gov/image-article/apod/apod-2026-august-23-cassini-approaches-saturn/"  # youtube


def main() -> None:
    address = "https://science.nasa.gov/apod/"
    response = requests.get(url=address)

    tree = LexborHTMLParser(html=response.content)
    node = tree.css_first("main")

    warning = False
    if node:
        media_node = node.css_first("img") or node.css_first(
            "source") or node.css_first("iframe")

        if media_node:
            media_title = node.css_first(
                "h1.display-48.margin-top-0.margin-bottom-3, h2.display-48.margin-top-0.margin-bottom-3").text()
            media_src = media_node.attrs['src'].split("?")[0]
            media_type = media_node.tag

            explanation = re.sub(
                pattern=r"\s*Explanation\s*:?\s*|\s(?=\s)|\s(?=[!',\.:;\?])",
                repl="",
                string=LexborHTMLParser(
                    html=node.css_first(
                        "p.media-detail-hero__description").html.split("<br")[0]
                ).text(),
                flags=re.I,
            )

            if media_type == "img":
                file_name = "apod" + os.path.splitext(media_src)[-1]
                media_alt = media_node.attrs['alt']
                media_bytes = requests.get(url=media_src).content

                client.files_upload_v2(
                    filename=file_name,
                    file=media_bytes,
                    title=media_title,
                    alt_txt=explanation,
                    channel=CHANNEL,
                )

            elif media_type == "source" or media_type == "iframe":
                media_alt = tree.css_first(
                    "meta[property=\"og:image:alt\"]").attributes.get("content")

                if media_type == "source":
                    media_url = tree.css_first(
                        "meta[property=\"og:image\"").attributes.get("content")
                    video_url = media_src

                else:
                    video_id = re.search(
                        pattern=r"youtu(?:\.be|be.com).*?/([\w\-]{11})",
                        string=media_src,
                        flags=re.I
                    )

                    if video_id:
                        media_url = f"https://i.ytimg.com/vi/{video_id.group(1)}/hqdefault.jpg"
                        video_url = f"https://www.youtube.com/watch?v={video_id.group(1)}"

                    else:
                        warning = True
                        logger.warning("no video id found")

                block: list[blocks.Block] = [
                    blocks.ImageBlock(
                        alt_text=media_alt,
                        image_url=media_url,
                        title=media_title,
                    ),
                    blocks.SectionBlock(
                        text=explanation,
                        accessory=blocks.LinkButtonElement(
                            text="Watch video",
                            url=video_url,
                        )
                    )
                ]

                client.chat_postMessage(
                    channel=CHANNEL,
                    text=media_title,
                    blocks=block,
                    unfurl_links=False,
                    unfurl_media=False,
                )

            else:
                warning = True
                logger.warning("media type not found")

        else:
            warning = True
            logger.warning("media node not found")

    else:
        warning = True
        logger.warning("main node not found")

    if warning:
        client.chat_postMessage(
            channel=CHANNEL,
            text=f"apod not found\n{address}",
            unfurl_links=False,
            unfurl_media=False,
        )


if __name__ == "__main__":
    main()
