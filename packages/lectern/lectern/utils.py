__all__ = [
    "is_path",
]


from urllib.parse import urlparse


def is_path(url: str) -> bool:
    return urlparse(url).path == url
