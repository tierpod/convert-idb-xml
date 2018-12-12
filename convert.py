#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from datetime import datetime

from lxml import etree, objectify


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT")
    return parser.parse_args()


def parse_xml(path):
    with open(path, "rb") as f:
        xml = f.read()

    result = []
    root = objectify.fromstring(xml)
    for blogpost in root.iterchildren():
        for comment in blogpost.comments.iterchildren():
            result.append({
                "id": "idb_%s" % str(comment.get("id")),
                "pid": "idb_%s" % str(comment.get("parentid")),
                "text": "<p>%s</p>" % str(comment["text"]),
                "user": {
                    "name": str(comment["name"]),
                    "id": "idb_%s" % str(comment["name"]).replace(" ", "_"),
                    "picture": "",
                    "admin": False,
                    "ip": str(comment["ip"]),
                },
                "locator": {
                    "site": "radiot",
                    "url": str(comment["url"]),
                },
                "score": str(comment["score"]),
                "votes": {},
                "time": convert_date(str(comment["gmt"])),
            })
    return result


def convert_date(s):
    # 2007-09-04 19:30:45
    d = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    return d.isoformat() + "Z"


def main():
    args = parse_args()
    data = parse_xml(args.INPUT)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

