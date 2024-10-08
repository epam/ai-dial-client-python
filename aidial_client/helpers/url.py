from aidial_client._constants import API_PREFIX


def enforce_trailing_slash(url: str) -> str:
    if url.endswith("/"):
        return url
    return url + "/"


def remove_leading_slash(url: str) -> str:
    if url.startswith("/"):
        return url.lstrip("/")
    return url


def remove_api_prefix(url):
    if url.startswith(API_PREFIX):
        api_prefix_len = len(API_PREFIX)
        url = url[api_prefix_len:]
    return url
