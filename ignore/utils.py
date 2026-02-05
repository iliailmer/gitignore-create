import requests
from typing import List


def get_file(names: List[str]):
    names_ = ",".join(names)
    url = f"https://www.toptal.com/developers/gitignore/api/{names_}"
    return requests.get(
        url,
        timeout=10,
    )


def get_template_list() -> List[str]:
    """Fetch list of available templates from API"""
    url = "https://www.toptal.com/developers/gitignore/api/list"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text.strip().split(',')


def search_templates(query: str) -> List[str]:
    """Search for templates matching query"""
    templates = get_template_list()
    return [t for t in templates if query.lower() in t.lower()]
