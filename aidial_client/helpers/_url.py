def enforce_trailing_slash(url: str) -> str:
    if url.endswith("/"):
        return url
    return url + "/"


def remove_prefix(s: str, prefix: str) -> str:
    if s.startswith(prefix):
        s = s.lstrip(prefix)
    return s


def remove_leading_slash(url: str) -> str:
    return remove_prefix(url, "/")
