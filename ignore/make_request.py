import requests


def make_request():
    return requests.get(
        "https://www.toptal.com/developers/gitignore/api/list?format=json"
    )
