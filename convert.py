#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from datetime import datetime

from lxml import etree, objectify


UNKNOWN_URL = "https://radio-t.com/old_comments_idb"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT")
    parser.add_argument("--print-empty-urls", action="store_true")
    return parser.parse_args()


class Comment(object):
    _title = ""
    _comment = {}

    def __init__(self, titles, blogpost, comment):
        self._title = str(blogpost["title"])
        url = extract_url(titles, self._title)
        parent_id = str(comment.get("parentid"))
        if parent_id == "0":
            parent_id = ""
        else:
            parent_id = "idb_%s" % parent_id
        self._comment = {
            "id": "idb_%s" % str(comment.get("id")),
            "pid": parent_id,
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
            "score": int(comment["score"]),
            "votes": {},
            "time": convert_date(str(comment["gmt"])),
        }


    def to_json(self):
        return json.dumps(self._comment, ensure_ascii=False)


    def is_unknown_url(self):
        return self._comment["locator"]["url"] == UNKNOWN_URL


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
            result.append(Comment(blogpost=blogpost, comment=comment, titles=titles))

    return result


def extract_url(titles, title):
    title = title.strip().lower().replace("#", "").replace("&ndash;", "–") \
        .replace("tемы", "темы") \
        .replace("запись и трансляция", "радио-t").replace("запись радио-t", "радио-t")
    for t in titles:
        tt = t["title"].strip().lower()
        if title.startswith(tt):
            return t["url"]

    return UNKNOWN_URL


def convert_date(s):
    # 2007-09-04 19:30:45
    d = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    return d.isoformat() + "Z"


def main():
    args = parse_args()
    result = parse_xml(args.INPUT)
    if args.print_empty_urls:
        for i in result:
            if i.is_unknown_url():
                print(i.to_json())
    else:
        for i in result:
            print(i.to_json())


if __name__ == "__main__":
    main()

