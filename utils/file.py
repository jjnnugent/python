from logging.config import fileConfig
import logging
import json
import os


def save_json(data, name) -> None:
    with open(file=name, mode="w", encoding="utf-8") as file:
        json.dump(obj=data, fp=file, indent=2)
    fileConfig(os.path.expanduser("~/logs/logging.conf"))
    logger = logging.getLogger("file--")
    logger.info("%s saved", os.path.basename(name))


def load_json(name) -> list | dict:
    with open(file=name, mode="r", encoding="utf-8") as file:
        data = json.load(fp=file)
    return data
