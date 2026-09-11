import asyncio
import pandas as pd
import json
import os

from py_gasbuddy import GasBuddy


sauce = [
    {
        "lat": 45.547363,  # ja
        "lon": -122.878416,
        "extra": [(9216, 3), (154636, 5), (177923, 12.5)]
    },
    {
        "lat": 35.584419,  # ma
        "lon": -97.614776,
        "extra": [(198759, 7)]
    },
    {
        "lat": 37.090726,  # mi
        "lon": -94.466266
    },
    {
        "lat": 34.171491,  # pp
        "lon": -118.335767
    }
]

fsolver = "http://192.168.50.5:8191/v1"


async def main():
    gb = GasBuddy(solver_url=fsolver)

    data = []
    for name in sauce:
        response = await gb.price_lookup_service(
            lat=name.get("lat"),
            lon=name.get("lon"),
            limit=6
        )

        if name.get("extra"):
            for s in name['extra']:
                temp = await GasBuddy(
                    station_id=s[0],
                    solver_url=fsolver
                ).price_lookup()

                temp['distance'] = s[1]
                data.append(temp)

        data += response['results']

    with open(file=os.path.expanduser("~/data/gas_prices.json"), mode="w") as file:
        json.dump(obj=data, fp=file, indent=2)

    return data


if __name__ == "__main__":
    data = asyncio.run(main())

    region = []
    href = []

    name = []
    distance = []
    reg = []
    mid = []
    prem = []

    for station in data:
        if station.get("regular_gas", {}).get("price") is None:
            continue

        address = station.get("address")
        street = address.get("line1")
        city = address.get("locality")
        state = address.get("region")
        zip = address.get("postalCode")
        region.append(state)

        href_maps = "https://www.google.com/maps/search/"
        href_street = street + "%2C" + city + "%2C" + \
            state + "+" + zip
        href_street = href_street.replace(" ", "+")
        href_url = f"[{street}]({href_maps}{href_street})"
        href.append(href_url)

        name.append(station.get("name"))
        distance.append(station.get("distance"))
        reg.append(station.get("regular_gas", {}).get("price", 0))
        mid.append(station.get("midgrade_gas", {}).get("price", 0))
        prem.append(station.get("premium_gas", {}).get("price", 0))

    result = {
        "reg": reg,
        "mid": mid,
        "prem": prem,
        "name": name,
        "addr": href,
        "state": region,
        "dist": distance,
    }

    df = pd.DataFrame(result)
    df.to_json(os.path.expanduser("~/data/df_gas_prices.json"))
