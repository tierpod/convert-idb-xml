#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
from datetime import datetime
from urllib.parse import unquote

import requests
from lxml import objectify


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
                    #"url": unquote(str(blogpost["url"])),
                    "url": get_url(str(blogpost["title"])),
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


API_GET_PODCAST = "https://radio-t.com/site-api/podcast/{num}"
RE_TITLE_NUM = re.compile(r"#(\d{1,3})$")
URLS_CACHE = {}

def get_url(podcast_title):
    num = RE_TITLE_NUM.findall(podcast_title)
    if not num:
        raise ValueError("unable to extract podcast number from title")

    num = num[0]
    if num in URLS_CACHE:
        return URLS_CACHE[num]

    r = requests.get(API_GET_PODCAST.format(num=num))
    url = r.json()["url"]
    URLS_CACHE[num] = url
    return url


def main():
    args = parse_args()
    data = parse_xml(args.INPUT)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

