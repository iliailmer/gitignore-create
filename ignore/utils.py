import requests
from typing import List


def get_all():
    return requests.get(
        "https://www.toptal.com/developers/gitignore/api/list?format=json",
        timeout=10,
    )


def get_file(names: List[str]):
    names_ = ",".join(names)
    url = f"https://www.toptal.com/developers/gitignore/api/{names_}"
    return requests.get(
        url,
        timeout=10,
    )
