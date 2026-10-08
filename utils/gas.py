import os
import re

from dotenv import load_dotenv
import pandas as pd


def gas(user_id: str) -> str:
    df = pd.read_json(os.path.expanduser("~/data/df_gas_prices.json"))

    load_dotenv(os.path.expanduser("~/python/.env"))
    if user_id == os.getenv("GAS_OR"):
        df = df.loc[df['state'] == "OR"]
        df = df.drop(columns=['mid', 'state'], inplace=False)
        df = df.sort_values(by=['prem'], inplace=False)
    elif user_id == os.getenv("GAS_OK"):
        df = df.loc[df["state"] == "OK"]
        df = df.drop(columns=['mid', 'prem', 'state'], inplace=False)
        df = df.sort_values(by=['reg'], inplace=False)
    elif user_id == os.getenv("GAS_MO"):
        df = df.loc[df["state"] == "MO"]
        df = df.drop(columns=['mid', 'prem', 'state'], inplace=False)
        df = df.sort_values(by=['reg'], inplace=False)
    elif user_id == os.getenv("GAS_CA"):
        df = df.loc[df["state"] == "CA"]
        df = df.drop(columns=['mid', 'state'], inplace=False)
        df = df.sort_values(by=['reg'], inplace=False)

    df = df.round(2)

    table_block = "|" + "|".join(df.columns.tolist()) + "|"
    table_block += "\n|" + ("---|" * len(df.columns))

    for row in df.itertuples(index=False):
        cells = []
        for cell in row:
            cells.append(str(cell))

        table_block += "\n|" + "|".join(cells) + "|"

    return table_block
