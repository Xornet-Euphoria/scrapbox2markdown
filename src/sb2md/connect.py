from sb2md.parse import parse_text
from typing import List
from requests import get
import typing
import json


def get_text(project: str, title: str, is_private: bool=False, sid: str=None) -> str:
    if is_private and sid is None:
        raise ValueError("`sid` must specified when you connect to private project.")
    cookies={"connect.sid": sid} if is_private else {}
    target = f"https://scrapbox.io/api/pages/{project}/{title}/text"
    r = get(target, cookies=cookies)

    if r.status_code == 200:
        return r.text

    error_codes = [401, 403, 404]

    err = json.loads(r.text)
    if r.status_code in error_codes:
        raise Exception(f"{err['name']}: {err['message']}")

    raise Exception(f"unknown error: response is here\n\t{err}")

