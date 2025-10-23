import json
import os

def save_json(data, name) -> None:
    with open(file=os.path.expanduser("~/data/") + name, mode="w", encoding="utf-8") as file:
        json.dump(obj=data, fp=file, indent=2)
