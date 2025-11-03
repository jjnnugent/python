import pandas as pd
import json
import os


def pm(text: str) -> str:
    with open(file=os.path.expanduser("~/data/cdata.json"), mode="r", encoding="utf-8") as file:
        cdata = json.load(fp=file)

    with open(file=os.path.expanduser("~/data/gdata.json"), mode="r", encoding="utf-8") as file:
        gdata = json.load(fp=file)

    name = list()
    multi = list()
    single = list()
    socket = list()
    for item in cdata['data']:
        name.append(item.get("name"))
        multi.append(int(item.get("cpumark").replace(",", "")) if item.get("cpumark") != "NA" else item.get("cpumark"))
        single.append(int(item.get("thread").replace(",", "")) if item.get("thread") != "NA" else item.get("thread"))
        socket.append(item.get("socket"))

    cdata = pd.DataFrame(
        {
            "name": name,
            "multi": multi,
            "single": single,
            "socket": socket
        }
    )

    name = list()
    score = list()
    for item in gdata['data']:
        name.append(item.get("name"))
        score.append(int(item.get("g3d").replace(",", "")) if item.get("g3d") != "NA" else item.get("g3d"))

    gdata = pd.DataFrame(
        {
            "name": name,
            "score": score
        }
    )

    if len(text) == 0:
        cdata.sort_values(by=['multi'], ascending=False, inplace=True)
        gdata.sort_values(by=['score'], ascending=False, inplace=True)
        result = cdata.to_string(index=False) + "\n\n" + gdata.to_string(index=False)
        return f"```{result}```"

    cmask = cdata['name'].str.contains(rf"{text}", case=False, regex=True) | cdata['socket'].str.contains(rf"{text}", case=False, regex=True)
    cdf = cdata[cmask]

    gmask = gdata['name'].str.contains(rf"{text}", case=False, regex=True)
    gdf = gdata[gmask]

    cdf.sort_values(by=['single'], ascending=False, inplace=True)
    gdf.sort_values(by=['score'], ascending=False, inplace=True)

    result = str()

    if not cdf.empty:
        result += cdf.to_string(index=False)
    if not gdf.empty:
        if len(result) > 0:
            result += "\n\n"
        result += gdf.to_string(index=False)
    if len(result) == 0:
        return f"{text} not found"

    return f"```{result}```"
