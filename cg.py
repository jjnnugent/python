import os
import random
import time

from curl_cffi import requests
from dotenv import load_dotenv
import pandas as pd

from utils.file import load_json
from utils.file import save_json
from utils.slack import slack_message


def check_gas_price(numbers: list) -> list:
    result = []
    for number in numbers:
        address = "https://www.costco.com/" + \
            "AjaxGetGasPricesService?warehouseid=" + \
            str(number)

        seconds = random.randint(2, 4)
        time.sleep(seconds)

        response = requests.get(url=address, impersonate="chrome")
        if response.status_code == 200:
            dump = response.json()
            result.append(dump)

    return result


def main() -> None:
    old = load_json(os.path.expanduser("~/data/cg.json"))
    dump = check_gas_price([9, 111, 692])

    if old != dump:
        save_json(data=dump, name=os.path.expanduser("~/data/cg.json"))

        locs = list()
        prem = list()
        reg = list()

        for item in dump:
            for key, value in item.items():
                locs.append(key)
                prem.append(item[key].get("premium"))
                reg.append(item[key].get("regular"))

        data = {
            "locations": locs,
            "premium": prem,
            "regular": reg,
        }

        df = pd.DataFrame(data)
        df['locations'] = df['locations'].replace(
            to_replace="692", value="Hillsboro")
        df['locations'] = df['locations'].replace(
            to_replace="9", value="Aloha")
        df['locations'] = df['locations'].replace(
            to_replace="111", value="Tigard")
        df = df.sort_values(by=['premium'], ascending=True)

        message = df.to_string(index=False)
        mobile_heading = f"{df['premium'].iloc[0]} {df['locations'].iloc[0]}"

        block = [
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_preformatted",
                        "elements": [
                            {
                                "type": "text",
                                "text": message
                            }
                        ]
                    }
                ]
            }
        ]

        load_dotenv(os.path.expanduser("~/python/.env"))
        slack_message(
            passw=os.getenv("WATCHER_TOKEN"),
            channel="D06G24QH97W",
            # channel=os.getenv("SANDBOX_CHANNEL"),
            blocks=block,
            text=mobile_heading
        )


if __name__ == "__main__":
    main()
