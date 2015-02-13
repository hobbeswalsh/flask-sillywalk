import sys

PY3 = sys.version_info[0] == 3
PY2 = sys.version_info[0] == 2

if PY2:
    from urlparse import urlparse

    s = lambda x: x

if PY3:
    from urllib.parse import urlparse

    s = lambda x: str(x, "utf-8")
