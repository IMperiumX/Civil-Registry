from hashlib import md5 as _md5
from typing import Any

from django.utils.encoding import force_bytes


def md5_text(*args: Any):
    m = _md5()  # noqa: S324
    for x in args:
        m.update(force_bytes(x, errors="replace"))
    return m
