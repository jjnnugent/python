import json

def save_json(data, name) -> None:
    with open(file=name, mode="w", encoding="utf-8") as file:
        json.dump(obj=data, fp=file, indent=2)

def load_json(name) -> list | dict:
    with open(file=name, mode="r", encoding="utf-8") as file:
        return json.load(fp=file)
