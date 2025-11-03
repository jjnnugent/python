import os

from utils.file import load_json
from utils.file import save_json
from utils.slack import slack_message

BOT = os.getenv("WATCHER_TOKEN")
CHANNEL = os.getenv("GAMING_CHANNEL")


def main() -> None:
    videos = load_json(os.path.expanduser("~/data/xbl.json"))
    if videos:
        videos[0] += 1
        title = f"Bob's XBL Clip Vault #{videos[0]}/114\n{videos.pop()}"
        sent = slack_message(
            timing=True,
            passw=BOT,
            channel=CHANNEL,
            unfurl_media=True,
            text=title,
        )

        if sent:
            save_json(data=videos, name=os.path.expanduser("~/data/xbl.json"))


if __name__ == "__main__":
    main()
