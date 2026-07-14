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
                cpu.append(item['specs'].get("cpu"))
                gpu.append(item['specs'].get("gpu").replace(
                    "NVIDIA", "GeForce") + " Laptop GPU")
                mem.append(item['specs'].get("ram"))
                name.append(item.get("title"))
                price.append(item.get("currentPrice") / 100)
                screen.append(item['specs'].get("screen"))
                storage.append(item['specs'].get("storage"))
                url.append(item.get("retailerUrl"))

            except Exception as e:
                logger.error("df list gen fail\n%s", e)

        name.append("JAK")
        url.append("n/a")
        cpu.append("Intel Core i9-13900HX")
        gpu.append("GeForce RTX 4080 Laptop GPU")
        mem.append("16-5600")
        screen.append("16\" 1600 240Hz")
        storage.append("512GB")
        price.append(1799.99)

        name.append("LIN")
        url.append("n/a")
        cpu.append("Intel Core i7-12800H")
        gpu.append("GeForce RTX 3080 Ti Laptop GPU")
        mem.append("32-4800")
        screen.append("15\" 1080 360Hz")
        storage.append("1TB")
        price.append(1759.20)

        name.append("MAK")
        url.append("n/a")
        cpu.append("Intel Core i7-11800H @ 2.30GHz")
        gpu.append("GeForce RTX 3070 Laptop GPU")
        mem.append("16-2933")
        screen.append("15\" 1080 360Hz")
        storage.append("1TB")
        price.append(1263.50)

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
            pat=r"\s*-\s*\d*GB", repl="", case=False, regex=True)

        frame = gld_df.join(cpu_df.set_index("model"), on="cpu")
        df = frame.join(gpu_df.set_index("model"), on="gpu")

        # df['link'] = df['link'].str.replace(
        #     pat=r"^(.*)$", repl="[\1](\1)", case=False, regex=True)

        df['cppd'] = round(df['multi'] / df['price'], 3)
        df['gppd'] = round(df['score'] / df['price'], 3)
        df['tppd'] = round((df['multi'] + df['score']) / df['price'], 3)

        # cpu.append("Intel Core i7-11800H @ 2.30GHz")
        remove_text = [
            r"Intel Core(?:\s*Ultra)?\s*i?\d\-?\s*",
            r"AMD\s*",
            r"\s*@\s*\d+\.\d+GHz",
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
            # channel=os.getenv("GAMING_CHANNEL"),
            channel=os.getenv("SANDBOX_CHANNEL"),
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
