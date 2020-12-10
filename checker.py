"""Simple script to find recursively files that have an invalid NTFS name.

This small script allows you to list them, and eventually, rename them.

See: https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file#naming-conventions
"""

import argparse
import logging
import re
import os
import sys

from glob import glob
from pathlib import Path


logger = logging.getLogger()
logger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


_INVALID_CHARS = re.escape("".join(chr(i) for i in range(32)) + '<>:"/\|?*')
_INVALID_CHARS_PATTERN = re.compile(f"[{_INVALID_CHARS}]")


def contains_invalid_chars(filename):
    invalid_char_match = _INVALID_CHARS_PATTERN.search(filename)

    return invalid_char_match is not None


def has_invalid_name(filename):
    bad_ending = filename.endswith(" ") or filename.endswith(".")
    return bad_ending or contains_invalid_chars(filename)


def get_curated_name(filename, sub_string):
    new_filename = _INVALID_CHARS_PATTERN.sub(sub_string, filename.strip())

    return new_filename


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("base_path", help="path to recursively search for files with invalid name", type=str)
    parser.add_argument("-s", "--sub_string", help="substitute invalid chars with this string", type=str, default="_")
    parser.add_argument("-q", "--quite", help="do not print to stdout", action="store_true")
    parser.add_argument("-r", "--rename", help="rename files and dirs with string", action="store_true")

    args = parser.parse_args()

    if args.quite:
        logger.removeHandler(stdout_handler)

    paths_to_rename = [
        path for path in Path(args.base_path).rglob("*")
        if has_invalid_name(path.name)
    ]

    for path in paths_to_rename[::-1]:
        logger.info("Invalid path: '%s'", path)

        if args.rename:
            new_path = path.parent / get_curated_name(path.name, args.sub_string)
            path.rename(new_path)
            logger.info("Renamed to '%s'", new_path)
