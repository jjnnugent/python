from dotenv import load_dotenv
import json
import os
import pandas as pd
import re

load_dotenv(os.path.expanduser("~/python/.env"))


def is_float(n) -> bool:
    try:
        float(n)
    except ValueError:
        return False
    return True


def gld(text="", csv=False) -> None | str:
    with open(
        file=os.path.expanduser("~/data/gld.json"), mode="r", encoding="utf-8"
    ) as file:
        gld = json.load(fp=file)

    # with open(
    #     file=os.path.expanduser("~/data/bgl.json"), mode="r", encoding="utf-8"
    # ) as file:
    #     bgl = json.load(fp=file)

    with open(
        file=os.path.expanduser("~/data/thw.json"), mode="r", encoding="utf-8"
    ) as file:
        thw = json.load(fp=file)

    with open(
        file=os.path.expanduser("~/data/ibp.json"), mode="r", encoding="utf-8"
    ) as file:
        ibp = json.load(fp=file)

    with open(
        file=os.path.expanduser("~/data/pcg.json"), mode="r", encoding="utf-8"
    ) as file:
        pcg = json.load(fp=file)

    with open(
        file=os.path.expanduser("~/data/cdata.json"), mode="r", encoding="utf-8"
    ) as file:
        cdata = json.load(fp=file)

    with open(
        file=os.path.expanduser("~/data/gdata.json"), mode="r", encoding="utf-8"
    ) as file:
        gdata = json.load(fp=file)

    name = list()
    multi = list()

    for item in cdata["data"]:
        model = item.get("name")
        model = re.sub(pattern=r"\s*@.*$", repl="", string=model, flags=re.I)
        name.append(model)
        multi.append(int(item.get("cpumark").replace(",", "")))

    cdata_df = pd.DataFrame({"name": name, "multi": multi})

    name = list()
    score = list()

    for item in gdata["data"]:
        name.append(item.get("name"))
        score.append(int(item.get("g3d").replace(",", "")))

    gdata_df = pd.DataFrame({"name": name, "score": score})

    if len(text) > 0:
        if text.startswith("$"):
            text = text[1:]
        query = text.split(maxsplit=1)
        if len(query) < 2 or len(query) > 2:
            return "invalid criteria\n`/gld 420.69 13900$|4080 laptop`"

        print(query)
        # query[0].replace("$", "")
        if not is_float(query[0]):
            print(query)
            return "price not found"

        find_cpu = cdata_df["name"].str.contains(
            pat=rf"{query[1]}", case=False, regex=True
        )
        if cdata_df[find_cpu].empty:
            return "cpu not found"

        find_gpu = gdata_df["name"].str.contains(
            pat=rf"{query[1]}", case=False, regex=True
        )
        if gdata_df[find_gpu].empty:
            return "gpu not found"

        find_cpu = (
            cdata_df[find_cpu].reset_index(drop=True).rename(columns={"name": "cpu"})
        )
        find_gpu = (
            gdata_df[find_gpu].reset_index(drop=True).rename(columns={"name": "gpu"})
        )

        query_df = pd.concat([find_cpu, find_gpu], axis=1)
        query_df["cost"] = float(query[0])
        query_df["brand"] = ""
        query_df["ram"] = ""
        query_df["screen"] = ""
        query_df["ssd"] = ""
        query_df["cppd"] = round(query_df["multi"] / query_df["cost"], 3)
        query_df["gppd"] = round(query_df["score"] / query_df["cost"], 3)
        query_df["tppd"] = round(
            (query_df["multi"] + query_df["score"]) / query_df["cost"], 3
        )
        query_df["*"] = "←"

    src = list()
    link = list()
    brand = list()
    cpu = list()
    gpu = list()
    mem = list()
    screen = list()
    ssd = list()
    price = list()

    src.append("JAK")
    link.append("")
    brand.append("Legion Pro 7 16lrx8h")
    cpu.append("Intel Core i9-13900HX")
    gpu.append("GeForce RTX 4080 Laptop GPU")
    mem.append("16-5600")
    screen.append("1600 240")
    ssd.append("512GB")
    price.append(float("1799.99"))

    src.append("LIN")
    link.append("")
    brand.append("2022 Blade 15")
    cpu.append("Intel Core i7-12800H")
    gpu.append("GeForce RTX 3080 Ti Laptop GPU")
    mem.append("32-4800")
    screen.append("1080 360")
    ssd.append("1TB")
    price.append(float("1759.20"))

    src.append("MAK")
    link.append("")
    brand.append("2021 Blade 15")
    cpu.append("Intel Core i7-11800H")
    gpu.append("GeForce RTX 3070 Laptop GPU")
    mem.append("16-2933")
    screen.append("1080 360")
    ssd.append("1TB")
    price.append(float("1263.50"))

    for item in gld:
        src.append("GLD")
        link.append(item["value"].get("deal_url"))
        brand.append(item["value"].get("laptop_name"))
        cpu_name = item["value"].get("cpu")
        gpu_name = item["value"].get("gpu")
        cpu_name = cpu_name.replace("I7", "i7")
        cpu.append(cpu_name)
        if gpu_name == "NVIDIA RTX 2050":
            gpu.append("GeForce RTX 2050")
        else:
            gpu.append(gpu_name)
        mem.append(item["value"].get("memory"))
        screen.append(item["value"].get("screen"))
        ssd.append(item["value"].get("storage"))
        price.append(float(item["value"].get("sale_price")))

    print("gld")
    print(len(src))
    print(len(link))
    print(len(brand))
    print(len(cpu))
    print(len(gpu))
    print(len(mem))
    print(len(screen))
    print(len(ssd))
    print(len(price))

    # for item in bgl["configs"]:
    #     src.append("BGL")
    #     brand.append(item.get("productTitle"))
    #     link.append(item.get("activeAffiliateLink"))
    #     price.append(float(item.get("currentPrice")))
    #     hz = "NA"
    #     mem_amount = "NA"
    #     mem_speed = "NA"
    #     res = "NA"
    #     for prop in item["properties"]:
    #         if prop.get("propertyTitle") == "Storage":
    #             ssd.append(prop.get("value"))
    #         if prop.get("propertyTitle") == "Display Refresh Rate (Hz)":
    #             hz = prop.get("value")
    #         if prop.get("propertyTitle") == "Display Resolution":
    #             res = prop.get("value")
    #         if prop.get("propertyTitle") == "Memory Amount":
    #             mem_amount = re.sub(
    #                 pattern=r"\s*GB", repl="", string=prop.get("value"), flags=re.I
    #             )
    #         if prop.get("propertyTitle") == "Memory Speed":
    #             mem_speed = re.sub(
    #                 pattern=r"\s*MHZ|\s*MT/S",
    #                 repl="",
    #                 string=prop.get("value"),
    #                 flags=re.I,
    #             )
    #         if prop.get("propertyTitle") == "Graphics Card":
    #             gpu_name = prop.get("value").strip()
    #             if gpu_name.startswith("RTX"):
    #                 gpu.append("NVIDIA " + gpu_name)
    #             else:
    #                 gpu.append(gpu_name)
    #
    #         if prop.get("propertyTitle") == "Processor":
    #             cpu_name = prop.get("value").strip()
    #             if cpu_name.startswith("Core"):
    #                 if "I" in cpu_name:
    #                     cpu_name = cpu_name.replace("I", "i")
    #                 cpu.append("Intel " + cpu_name)
    #             elif cpu_name.startswith("Ryzen"):
    #                 if "MAX" in cpu_name:
    #                     cpu_name = cpu_name.replace("MAX", "Max")
    #                 if cpu_name.endswith("HX 370"):
    #                     cpu_name = "Ryzen AI 9 HX 370"
    #                 cpu.append("AMD " + cpu_name)
    #             else:
    #                 cpu.append(cpu_name)
    #     mem.append(f"{mem_amount}-{mem_speed}")
    #     screen.append(f"{res} {hz}")
    #
    # print("bgl")
    # print(src)
    # print(link)
    # print(brand)
    # print(cpu)
    # print(gpu)
    # print(mem)
    # print(screen)
    # print(ssd)
    # print(price)
    # print(len(src))
    # print(len(link))
    # print(len(brand))
    # print(len(cpu))
    # print(len(gpu))
    # print(len(mem))
    # print(len(screen))
    # print(len(ssd))
    # print(len(price))
    # exit()

    for item in thw:
        src.append("THW")
        brand.append(item.get("brand"))
        price.append(float(item.get("price")))
        cpu_name = item.get("cpu")
        if cpu_name is not None:
            if cpu_name.startswith("Core"):
                cpu_name = "Intel " + cpu_name
            if cpu_name.startswith("Ryzen"):
                cpu_name = "AMD " + cpu_name
            if cpu_name.endswith("12500H"):
                cpu_name = cpu_name.replace("7", "5")
            cpu.append(cpu_name)
        else:
            cpu.append(cpu_name)
        gpu_name = item.get("gpu")
        if gpu_name is not None:
            if gpu_name.startswith("RTX"):
                gpu_name = "GeForce " + gpu_name + " Laptop GPU"
            gpu.append(gpu_name)
        else:
            gpu.append(gpu_name)
        mem.append(item.get("mem"))
        screen.append(None)
        ssd.append(item.get("ssd"))
        link.append(item.get("link"))

    print("thw")
    print(len(src))
    print(len(link))
    print(len(brand))
    print(len(cpu))
    print(len(gpu))
    print(len(mem))
    print(len(screen))
    print(len(ssd))
    print(len(price))

    for item in ibp:
        src.append("IBP")
        link.append(os.getenv("URL_IBPS") + item["FullContent"].get("Link"))
        brand.append(item["FullContent"].get("Name"))
        price.append(float(item["FullContent"].get("Price")))
        skus = item["FullContent"]["Skus"].keys()
        for sku in skus:
            option = item["FullContent"]["Skus"][sku].get("Option")
            name = item["FullContent"]["Skus"][sku].get("Name")
            if option == "Display":
                res = re.search(
                    pattern=r"\d+(?:\s*)?x(?:\s*)(\d+)", string=name, flags=re.I
                )
                hz = re.search(pattern=r"(\d+)(?=Hz)", string=name, flags=re.I)
                if res:
                    display = res.group(1)
                    if hz:
                        display += " " + hz.group(1)
                else:
                    display = "NA"
                screen.append(display)
            elif option == "Processor":
                cpu_name = re.sub(
                    pattern=r"®|™|D?\s*CPU", repl="", string=name, flags=re.I
                )
                cpu_name = cpu_name.replace("i5-13650HX", "i7-13650HX")
                cpu.append(cpu_name)
            elif option == "Memory":
                mem.append(
                    re.sub(
                        pattern=r"GB\s*DDR\d|MHz|\s*RAM",
                        repl="",
                        string=name,
                        flags=re.I,
                    )
                )
            elif option == "Video Card":
                gpu.append(
                    re.sub(
                        pattern=r"NVIDIA\s*|\s*-\s*\d+GB",
                        repl="",
                        string=name + " Laptop GPU",
                        flags=re.I,
                    )
                )
            elif option == "Primary Storage":
                ssd.append(
                    re.sub(
                        pattern=r"^(\d+[GT]B).*$", repl=r"\1", string=name, flags=re.I
                    )
                )
            else:
                continue

    print("ibp")
    print(len(src))
    print(len(link))
    print(len(brand))
    print(len(cpu))
    print(len(gpu))
    print(len(mem))
    print(len(screen))
    print(len(ssd))
    print(len(price))

    for item in pcg:
        src.append("PCG")
        brand.append(item.get("brand"))
        gpu_name = item.get("gpu")
        if gpu_name.startswith("RTX"):
            gpu_name = "GeForce " + gpu_name + " Laptop GPU"
        gpu.append(gpu_name)
        cpu_name = item.get("cpu")
        if cpu_name.startswith("Core"):
            cpu_name = "Intel " + cpu_name
        elif cpu_name.startswith("Ryzen"):
            cpu_name = "AMD " + cpu_name
            if cpu_name.endswith("9 HX 365"):
                cpu_name = "AMD Ryzen AI 9 HX 375"
        cpu_name = re.sub(pattern=r"(i\d)\s", repl=r"\1-", string=cpu_name, flags=re.I)
        cpu.append(cpu_name)
        mem.append(
            re.sub(pattern=r"^(\d+).*$", repl=r"\1", string=item.get("mem"), flags=re.I)
        )
        res = ""
        hz = re.search(
            pattern=r"(\d{3})", string=item.get("hz")
        ).group(1)
        screen.append(res + hz)
        ssd.append(
            re.sub(
                pattern=r"^(\d+[GT]B).*$",
                repl=r"\1",
                string=item.get("ssd").replace(" ", ""),
                flags=re.I,
            )
        )
        link.append(item.get("link"))
        price.append(float(item.get("price")))

    # print("pcg")
    # print(src)
    # print(link)
    # print(brand)
    # print(cpu)
    # print(gpu)
    # print(mem)
    # print(screen)
    # print(ssd)
    # print(price)
    # print(len(src))
    # print(len(link))
    # print(len(brand))
    # print(len(cpu))
    # print(len(gpu))
    # print(len(mem))
    # print(len(screen))
    # print(len(ssd))
    # print(len(price))
    # exit()

    gld_df = pd.DataFrame(
        {
            "link": link,
            "cost": price,
            "src": src,
            "brand": brand,
            "screen": screen,
            "ram": mem,
            "ssd": ssd,
            "cpu": cpu,
            "gpu": gpu,
        }
    )

    # Intel Core Ultra 7 240H
    # Intel Core Ultra 7 250H
    gld_df["cpu"] = gld_df["cpu"].str.replace(
        pat=r"^Intel Core Ultra 7 (2[45]0)H$",
        repl=r"Intel Core 7 \1H",
        case=False,
        regex=True,
    )

    # Intel Core Ultra 9 275HX
    gld_df["cpu"] = gld_df["cpu"].str.replace(
        pat=r"275\s*HX?$", repl="275HX", case=False, regex=True
    )

    # (?!2050)\d{4}
    gld_df["gpu"] = gld_df["gpu"].str.replace(
        pat=r"^NVIDIA.*?((?!2050)\d{4}.*)$",
        repl=r"GeForce RTX \1 Laptop GPU",
        case=False,
        regex=True,
    )

    gld_df["gpu"] = gld_df["gpu"].str.replace(
        pat=r"^AMD.*?(\d{4}[MS](?:\s+XT)?)$",
        repl=r"Radeon RX \1",
        case=False,
        regex=True,
    )

    frames = gld_df.join(cdata_df.set_index("name"), on="cpu")
    df = frames.join(gdata_df.set_index("name"), on="gpu")

    # points per dollar = ppd
    df["cppd"] = round(df["multi"] / df["cost"], 3)
    df["gppd"] = round(df["score"] / df["cost"], 3)
    df["tppd"] = round((df["multi"] + df["score"]) / df["cost"], 3)

    if len(text) > 1:
        df = pd.concat([df, query_df], ignore_index=True)

    df["brand"] = df["brand"].str.replace(
        pat=r"(?:\(\d{4}\))", repl="", case=False, regex=True
    )
    df["brand"] = df["brand"].str[:12]
    df["screen"] = df["screen"].str.replace(
        pat=r"^.*(\d{4})p?\s*(\d{3})(?:NA|HZ)?.*$", repl=r"\1 \2", case=False, regex=True
    )
    df["ram"] = df["ram"].str.replace(
        pat=r"(?:\s*GB\s*|(?:LP)?DDR5|\s*RAM|\s*M[HT]/?[SZ])",
        repl="",
        case=False,
        regex=True,
    )
    df["ssd"] = df["ssd"].str.replace(pat=r"SSD|\s*", repl="", case=False, regex=True)
    df["cpu"] = df["cpu"].str.replace(
        pat=r"^.*?(\w+)$", repl=r"\1", case=False, regex=True
    )
    df["gpu"] = df["gpu"].str.replace(
        pat=r"\s*(?:GeForce|RT?X|Laptop|GPU|Radeon)\s*", repl="", case=False, regex=True
    )

    cppd_do = df["cppd"].idxmin()
    cppd_up = df["cppd"].idxmax()
    df["cppd"] = df["cppd"].astype(dtype="str")

    for i in range(len(df["cppd"])):
        if i == cppd_do:
            df.loc[i, "cppd"] = df.loc[i, "cppd"] + "↓"
        elif i == cppd_up:
            df.loc[i, "cppd"] = df.loc[i, "cppd"] + "↑"
        else:
            df.loc[i, "cppd"] = df.loc[i, "cppd"] + " "

    gppd_do = df["gppd"].idxmin()
    gppd_up = df["gppd"].idxmax()
    df["gppd"] = df["gppd"].astype(dtype="str")

    for i in range(len(df["gppd"])):
        if i == gppd_do:
            df.loc[i, "gppd"] = df.loc[i, "gppd"] + "↓"
        elif i == gppd_up:
            df.loc[i, "gppd"] = df.loc[i, "gppd"] + "↑"
        else:
            df.loc[i, "gppd"] = df.loc[i, "gppd"] + " "

    df.sort_values(by=["tppd"], ascending=False, inplace=True)
    df = df.fillna(value="")

    if "*" in df.keys():
        df = df[
            [
                "cost",
                "cpu",
                "gpu",
                "multi",
                "score",
                "cppd",
                "gppd",
                "tppd",
                "src",
                "brand",
                "screen",
                "ram",
                "ssd",
                "*",
            ]
        ]
    elif csv:
        df = df[
            [
                "cost",
                "cpu",
                "gpu",
                "multi",
                "score",
                "cppd",
                "gppd",
                "tppd",
                "src",
                "brand",
                "screen",
                "ram",
                "ssd",
                "link",
            ]
        ]
    else:
        df = df[
            [
                "cost",
                "cpu",
                "gpu",
                "multi",
                "score",
                "cppd",
                "gppd",
                "tppd",
                "src",
                "brand",
                "screen",
                "ram",
                "ssd",
            ]
        ]

    # df["multi"] = df["multi"].astype("int32")
    df["cost"] = df["cost"].astype("str")
    df["score"] = df["score"].astype("str")
    df["cost"] = df["cost"].str.replace(pat=".0", repl="")
    df["score"] = df["score"].str.replace(pat=".0", repl="")
    df.rename(columns={"tppd": "tppd↓"}, inplace=True)

    df = df.reset_index(drop=True).set_axis(range(1, len(df) + 1))

    if csv:
        df.to_csv(
            path_or_buf=os.path.expanduser("~/data/gld.csv"),
            encoding="utf-8",
        )
    else:
        return f"```{df.to_string()}```"


def main() -> None:
    gld(csv=True)


if __name__ == "__main__":
    main()
