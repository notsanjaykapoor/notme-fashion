import base64
import json


def base64_to_json(s: str) -> dict:
    """ convert base64 string to json dict"""
    return json.loads(base64.b64decode(s).decode("utf-8"))
   