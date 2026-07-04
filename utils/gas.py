import os
import re

from dotenv import load_dotenv
import pandas as pd


def gas(user_id: str) -> str:
    data = pd.read_json(os.path.expanduser("~/data/gas_prices.json"))

    addr = []
    comm = []
    fhom = []
    fwor = []
    maps = []
    midg = []
    name = []
    regu = []
    prem = []

    if user_id == "U02S8PJP96H":
        username = "gas_ja"
        data = data['gas_ja'].get("results")
    elif user_id == "U02UJM0GXB3":
        username = "gas_ma"
        data = data['gas_ma'].get("results")
    elif user_id == "U02UB3REJ8M":
        username = "gas_mi"
        data = data['gas_mi'].get("results")
    elif user_id == "U0ABBJ1N6TU":
        username = "gas_pa"
        data = data['gas_pa'].get("results")

    for station in data:
        regular_price = station.get("regular_gas", {}).get("price")
        if regular_price is None:
            continue

        premium_price = station.get("premium_gas", {}).get("price")
        if premium_price is None and username == "gas_ja":
            continue

        station_id = station.get("station_id")
        address = station.get("address")
        city = address.get("locality")
        state = address.get("region")
        street = address.get("line1")
        zip = address.get("postalCode")

        addr.append(f"{street}, {city}, {state} {zip}")
        maps.append("[" + street + "](https://www.google.com/maps/search/" +
                    re.sub(pattern=r"\s+", repl="+", string=addr[-1], flags=re.I) + ")")

        name.append(station.get("name"))
        midg.append(station.get("midgrade_gas", {}).get("price"))
        prem.append(premium_price)
        regu.append(regular_price)

        station_ids = {
            "174512": {
                "home": 2.6,
                "work": 6.6,
                "comm": "N"
            },
            "146651": {
                "home": 7.4,
                "work": 1.7,
                "comm": "N"
            },
            "159906": {
                "home": 0.8,
                "work": 5.5,
                "comm": "Y"
            },
            "117879": {
                "home": 1.9,
                "work": 4.6,
                "comm": "Y"
            },
            "159905": {
                "home": 3.2,
                "work": 2.8,
                "comm": "Y"
            },
            "98773": {
                "home": 3.3,
                "work": 3.3,
                "comm": "Y"
            },
            "212649": {
                "home": 4.7,
                "work": 2.2,
                "comm": "Y"
            },
            "98772": {
                "home": 3.9,
                "work": 2.0,
                "comm": "Y"
            },
            "186001": {
                "home": 5.1,
                "work": 1.6,
                "comm": "Y"
            },
            "9216": {
                "home": 7.1
            },
            "154636": {
                "home": 4.2
            },
            "177923": {
                "home": 12.3
            },
            "198759": {
                "home": 7.5
            },
        }

        if station_id in station_ids.keys():
            fhom.append(station_ids[station_id].get("home"))
            fw = station_ids[station_id].get("work")
            com = station_ids[station_id].get("comm")
            if fw and com:
                fwor.append(fw)
                comm.append(com)
        else:
            fhom.append(station.get("distance"))

    df_data = {
        "REG": regu,
        "MID": midg,
        "PREM": prem,
        "NAME": name,
        "ADDRESS": maps,
        # "FH": fhom,
    }

    if fwor:
        df_data['C'] = comm
        df_data['FH'] = fhom
        df_data['FW'] = fwor
        del df_data['NAME']
        del df_data['MID']
        del df_data['PREM']
    else:
        df_data['FH'] = fhom

    if username == "gas_ja":
        del df_data['REG']
        del df_data['MID']
    elif username == "gas_ma":
        del df_data['MID']
        del df_data['PREM']

    df = pd.DataFrame(df_data)
    if username == "gas_ja":
        df = df.sort_values(by=['PREM'])
    else:
        df = df.sort_values(by=['REG'])
    df = df.round(2)
    df = df.head(6)

    table_block = "|" + "|".join(df.columns.tolist()) + "|"
    table_block += "\n|" + ("---|" * len(df_data))

    for row in df.itertuples(index=False):
        cells = []
        for cell in row:
            cells.append(str(cell))

        table_block += "\n|" + "|".join(cells) + "|"

    return table_block
