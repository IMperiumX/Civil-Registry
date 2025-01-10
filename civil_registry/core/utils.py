from __future__ import annotations

from datetime import datetime
from hashlib import md5 as _md5
from typing import Any

import time_machine
from django.utils.encoding import force_bytes


def md5_text(*args: Any):
    m = _md5()  # noqa: S324
    for x in args:
        m.update(force_bytes(x, errors="replace"))
    return m


def freeze_time(t: str | datetime | None = None) -> time_machine.travel:
    if t is None:
        t = datetime.now(datetime.UTC)
    return time_machine.travel(t, tick=False)
