from logging.config import fileConfig
import logging
import os

from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/python/.env"))
# slagger = logging.getLogger(name="slack_sdk.web.base_client")
# slagger.disabled = 1
#
# fileConfig(fname=os.path.expanduser("~/logs/logging.conf"))
# logger = logging.getLogger("------")
