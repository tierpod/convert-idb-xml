#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from datetime import datetime

from lxml import etree, objectify


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT")
    parser.add_argument("--print-empty-urls", action="store_true")
    return parser.parse_args()


def parse_xml(path):
    with open(path, "rb") as f:
        xml = f.read()


    with open("titles.json", "rb") as f:
        titles = json.load(f)

    result = []
    empty_urls = []
    root = objectify.fromstring(xml)
    for blogpost in root.iterchildren():
        for comment in blogpost.comments.iterchildren():
            url = extract_url(titles, str(blogpost["title"]))
            if not url:
                empty_urls.append({
                    "title": str(blogpost["title"]),
                    "id": str(comment.get("id")),
                    "pid": str(comment.get("parentid")),
                })

            result.append({
                "id": "idb_%s" % str(comment.get("id")),
                "pid": "idb_%s" % str(comment.get("parentid")),
                "text": "<p>%s</p>" % str(comment["text"]),
                "user": {
                    "name": str(comment["name"]),
                    "id": "idb_%s" % str(comment["name"]).replace(" ", "_"),
                    "picture": "",
                    "admin": False,
                    "ip": "",
                },
                "locator": {
                    "site": "radiot",
                    "url": url,
                },
                "score": str(comment["score"]),
                "votes": {},
                "time": convert_date(str(comment["gmt"])),
            })
    return result, empty_urls


def extract_url(titles, title):
    title = title.strip().lower().replace("#", "").replace("&ndash;", "–").replace("tемы", "темы")
    for t in titles:
        tt = t["title"].strip().lower()
        if title.startswith(tt):
            return t["url"]

    return ""


def convert_date(s):
    # 2007-09-04 19:30:45
    d = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    return d.isoformat() + "Z"


def main():
    args = parse_args()
    data, empty_urls = parse_xml(args.INPUT)
    if args.print_empty_urls:
        result = empty_urls
    else:
        result = data

    for i in result:
        print(i)


if __name__ == "__main__":
    main()

