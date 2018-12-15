#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT")
    return parser.parse_args()


def process_file(path):
    with open("titles.json", "rb") as f:
        titles = json.load(f)

    result = []
    for i in titles:
        if "podcast" in i["categories"]:
            num = extract_num(i["url"])
            result.append((num, i["url"]))

    return result


def extract_num(url):
    _, podcast, _ = url.rsplit("/", 2)
    num = podcast.replace("podcast-", "")
    return num


def main():
    args = parse_args()
    result = process_file(args.INPUT)

    for num, url in result:
        print("http://radio-t.com/podcasts/radio-t-{num}/ -> {url}".format(num=num, url=url))


if __name__ == "__main__":
    main()

