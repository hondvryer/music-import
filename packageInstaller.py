import sys
import os

packageList = [
    "fnmatch",
    "pathlib",
    "mutagen",
    "imghdr",
    "wave",
    "contextlib",
    "json",
    "uuid",
    "random",
    "builtins",
    "pymongo",
]
try:
    for package in packageList:
        os.system("pip install " + package)

except Exception as e:
    print(e)
