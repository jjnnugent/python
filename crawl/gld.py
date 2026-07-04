from logging.config import fileConfig

import logging
import os

from curl_cffi import requests
from dotenv import load_dotenv
from utils.file import load_json
from utils.file import save_json
from utils.slack import SlackHandler
from utils.slack import slack_message

import pandas as pd


load_dotenv(os.path.expanduser("~/python/.env"))
fileConfig(os.path.expanduser("~/logs/logging.conf"))
logger = logging.getLogger("gl-gld")
logger.addHandler(SlackHandler())
slagger = logging.getLogger(name="slack_sdk.web.base_client")
slagger.disabled = 1


def load_data() -> list:
    result = []
    address = os.getenv("URL_GLD")
    response = requests.get(url=address, impersonate="chrome")
    if response.status_code == 200:
        try:
            result = response.json()
        except Exception as e:
            logger.error(e)
    else:
        logger.warning("returned %s", response.status_code)

    return result


def markdown_table_block(df: pd.DataFrame) -> list:
    text = "|" + "|".join(df.columns) + "|"
    text += "\n|" + "---|" * len(df.columns)

    for row in df.itertuples(index=False):
        cells = []
        for cell in row:
            cells.append(str(cell))

        text += "\n|" + "|".join(cells) + "|"

    result = [
        {
            "type": "markdown",
            "text": text,
        }
    ]

    return result


def main() -> None:
    gld_new = load_data()
    gld_old = load_json(name=os.path.expanduser("~/data/gld.json"))

    if not gld_new:
        logger.error("no data found")

    elif gld_new == gld_old:
        logger.info("no updates")

    else:
        cpu_raw = load_json(name=os.path.expanduser("~/data/cdata.json"))
        gpu_raw = load_json(name=os.path.expanduser("~/data/gdata.json"))

        cpu_model = []
        cpu_score = []
        gpu_model = []
        gpu_score = []

        for item in cpu_raw['data']:
            if "Laptop" in item.get("cat") or "Mobile" in item.get("cat"):
                cpu_model.append(item.get("name"))
                cpu_score.append(int(item.get("cpumark").replace(",", "")))
            else:
                continue

        for item in gpu_raw['data']:
            if "Laptop" in item.get("cat") or "Mobile" in item.get("cat"):
                gpu_model.append(item.get("name"))
                gpu_score.append(int(item.get("g3d").replace(",", "")))
            else:
                continue

        cpu_df = pd.DataFrame({'model': cpu_model, 'multi': cpu_score})
        gpu_df = pd.DataFrame({'model': gpu_model, 'score': gpu_score})

        cpu = []
        gpu = []
        mem = []
        name = []
        price = []
        screen = []
        storage = []
        url = []

        for item in gld_new:
            try:
                cpu.append(item['value'].get("cpu"))
                gpu.append(item['value'].get("gpu").replace(
                    "NVIDIA", "GeForce") + " Laptop GPU")
                mem.append(item['value'].get("memory"))
                name.append(item['value'].get("laptop_name"))
                price.append(float(item['value'].get("sale_price")))
                screen.append(item['value'].get("screen"))
                storage.append(item['value'].get("storage"))
                url.append(item['value'].get("deal_url"))

            except Exception as e:
                logger.error("df list gen fail\n%s", e)

        try:
            gld_df = pd.DataFrame(
                {
                    "price": price,
                    "cpu": cpu,
                    "gpu": gpu,
                    "brand": name,
                    "screen": screen,
                    "mem": mem,
                    "ssd": storage,
                    "link": url,
                }
            )

        except Exception as e:
            logger.error(e)

        gld_df['gpu'] = gld_df['gpu'].str.replace(
            pat=r" - \d*GB", repl="", case=False, regex=True)

        frame = gld_df.join(cpu_df.set_index("model"), on="cpu")
        df = frame.join(gpu_df.set_index("model"), on="gpu")

        # df['link'] = df['link'].str.replace(
        #     pat=r"^(.*)$", repl="[\1](\1)", case=False, regex=True)

        df['cppd'] = round(df['multi'] / df['price'], 3)
        df['gppd'] = round(df['score'] / df['price'], 3)
        df['tppd'] = round((df['multi'] + df['score']) / df['price'], 3)

        remove_text = [
            r"Intel Core (?:Ultra)?\s*\d\s*",
            r"AMD\s*",
            r"Ryzen (?:AI)?\s*\d\s*",
            r"Radeon\s*RX\s*",
            "GeForce RTX ",
            " Laptop GPU",
            r"GB (?:LP)?DDR\dX?",
            " RAM",
            r" \d{4} x",
            " display",
            r" PCIe Gen \d",
            " SSD",
        ]

        df['brand'] = df['brand'].str.replace(
            pat=r"^(\w+).*$", repl=r"\1", case=False, regex=True)
        df = df.replace(to_replace="|".join(remove_text),
                        value="", inplace=False, regex=True)

        df = df[['price', 'cpu', 'gpu', 'multi', 'score', 'cppd', 'gppd', 'tppd',
                 'brand', 'screen', 'mem', 'ssd', 'link']]

        df.sort_values(by=['tppd'], ascending=False, inplace=True)
        table_block = markdown_table_block(df)

        sent = slack_message(
            timing=True,
            passw=os.getenv("WATCHER_TOKEN"),
            channel=os.getenv("GAMING_CHANNEL"),
            blocks=table_block,
            unfurl_links=False,
            text="Gaming Laptop Deals",
        )

        if sent:
            save_json(data=gld_new, name=os.path.expanduser("~/data/gld.json"))
        else:
            logger.error("not sent to slack")


if __name__ == "__main__":
    main()
