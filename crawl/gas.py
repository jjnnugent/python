import asyncio
import os
import re

from dotenv import load_dotenv
import pandas as pd
from py_gasbuddy import GasBuddy
from utils.file import load_json
from utils.file import save_json
from utils.slack import slack_message

load_dotenv(os.path.expanduser("~/python/.env"))


async def gas_ja():
    gb = GasBuddy(solver_url="http://localhost:8191/v1")
    data = await gb.price_lookup_service(
        lat=45.546533681862904,
        lon=-122.90002507313264,
        limit=10
    )

    # gb = GasBuddy(station_id=9216, solver_url="http://localhost:8191/v1")
    # costco1 = await gb.price_lookup()
    # data['results'].append(costco1)

    gb = GasBuddy(station_id=154636, solver_url="http://localhost:8191/v1")
    costco2 = await gb.price_lookup()
    data['results'].append(costco2)

    gb = GasBuddy(station_id=177923, solver_url="http://localhost:8191/v1")
    costco3 = await gb.price_lookup()
    data['results'].append(costco3)

    current_low = min([station['premium_gas'].get("price") if station['premium_gas'].get(
        "price") else 100 for station in data['results']])

    data['lowest'] = current_low
    return data


async def gas_ma():
    gb = GasBuddy(solver_url="http://localhost:8191/v1")
    data = await gb.price_lookup_service(
        lat=35.58443828824383,
        lon=-97.62049291423543,
        limit=10
    )

    gb = GasBuddy(station_id=198759, solver_url="http://localhost:8191/v1")
    costco = await gb.price_lookup()
    data['results'].append(costco)

    current_low = min([station['regular_gas'].get("price") if station['regular_gas'].get(
        "price") else 100 for station in data['results']])

    data['lowest'] = current_low
    return data


async def gas_mi():
    data = {}
    data['results'] = []

    stations = [
        "146651",
        "174512",
        "98773",
        "186001",
        "159905",
        "117879",
        "159906",
        "98772",
        "212649",
    ]

    for station in stations:
        gb = GasBuddy(station_id=station,
                      solver_url="http://localhost:8191/v1")
        station_json = await gb.price_lookup()
        data['results'].append(station_json)

    current_low = min([station['regular_gas'].get("price") if station['regular_gas'].get(
        "price") else 100 for station in data['results']])

    data['lowest'] = current_low
    return data


async def gas_pa():
    gb = GasBuddy(solver_url="http://localhost:8191/v1")
    data = await gb.price_lookup_service(
        lat=34.171394571814886,
        lon=-118.33634567313177,
        limit=10
    )

    current_low = min([station['regular_gas'].get("price") if station['regular_gas'].get(
        "price") else 100 for station in data['results']])

    data['lowest'] = current_low
    return data


new_data = {}
users = ['gas_ja', 'gas_ma', 'gas_mi', 'gas_pa']
new_data['gas_ja'] = asyncio.run(gas_ja())
new_data['gas_ma'] = asyncio.run(gas_ma())
new_data['gas_mi'] = asyncio.run(gas_mi())
new_data['gas_pa'] = asyncio.run(gas_pa())

old_data = load_json(name=os.path.expanduser("~/data/gas_prices.json"))

for user in users:
    new_user_low = new_data[user].get("lowest")
    old_user_low = old_data[user].get("lowest")

    if new_user_low == old_user_low:
        print("no change")

save_json(data=new_data, name=os.path.expanduser("~/data/gas_prices.json"))
