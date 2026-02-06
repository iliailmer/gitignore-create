import requests
from typing import List


API_BASE_URL = "https://www.toptal.com/developers/gitignore/api"


def get_file(names: List[str]) -> str:
    """
    Fetch gitignore template content for given language names.

    Args:
        names: List of language/template names

    Returns:
        Decoded template content as string (may contain error message if template not found)

    Raises:
        RuntimeError: If API request fails (network errors, timeouts, server errors)
    """
    names_ = ",".join(names)
    url = f"{API_BASE_URL}/{names_}"

    try:
        resp = requests.get(url, timeout=10)

        # The API returns 404 with error message in body for invalid templates
        # We want to return the body so callers can check for error message
        # Only raise for server errors (500+) or other issues
        if resp.status_code >= 500:
            raise RuntimeError(f"API server error: {resp.status_code}")

        return resp.content.decode("utf-8")
    except requests.exceptions.Timeout:
        raise RuntimeError(f"API request timed out after 10 seconds")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {str(e)}")


def get_template_list() -> List[str]:
    """
    Fetch list of available templates from API.

    Returns:
        Sorted list of template names

    Raises:
        RuntimeError: If API request fails
    """
    url = f"{API_BASE_URL}/list"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return sorted(resp.text.strip().split(','))
    except requests.exceptions.Timeout:
        raise RuntimeError(f"API request timed out after 10 seconds")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"API returned error: {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {str(e)}")


def search_templates(query: str) -> List[str]:
    """
    Search for templates matching query.

    Args:
        query: Search term

    Returns:
        Sorted list of matching template names
    """
    templates = get_template_list()
    return [t for t in templates if query.lower() in t.lower()]


def validate_gitignore_response(content: str) -> bool:
    """
    Check if gitignore response is valid or contains an error.

    The API returns errors in the format: "#!! ERROR: template is undefined !!#"

    Args:
        content: Response content to validate

    Returns:
        True if valid, False if error detected
    """
    return "#!! ERROR:" not in content
