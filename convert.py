#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import json
from datetime import datetime

from lxml import etree, objectify


UNKNOWN_URL = "https://radio-t.com/old_comments_idb"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT")
    parser.add_argument("--print-empty-urls", action="store_true")
    parser.add_argument("--filter-doubles", action="store_true")
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


    def id(self):
        s = (self._comment["text"] + self._comment["time"] + self._comment["user"]["name"])
        return hashlib.sha256(s.encode("utf-8")).hexdigest()


    def __eq__(self, item):
        if (self._comment["text"] == item._comment["text"]) \
            and (self._comment["time"] == item._comment["time"]) \
            and (self._comment["user"] == item._comment["user"]):
            return True

        return False


    def __str__(self):
        return "Comment(id=%s, pid=%s, user=%s, url=%s)" % (
            self._comment["id"], self._comment["pid"], self._comment["user"]["name"],
            self._comment["locator"]["url"],
        )


class GroupedComments(object):
    def __init__(self, comments):
        """
        Args:
            comments (list of Comment)
        """

        groups = {}
        for c in comments:
            cid = c.id()
            if cid in groups:
                groups[cid].append(c)
            else:
                groups[cid] = [c]

        self._groups = groups

    def to_dict(self):
        j = []
        for cid, group in self._groups.items():
            jj = {}
            jj["cid"] = cid
            jj["len"] = len(group)
            jj["comments"] = [g._comment for g in group]
            # for i in jj["comments"]:
            #     print(type(i), i)
            j.append(jj)
        return j

    def to_json(self, **kwargs):
        j = self.to_dict()
        return json.dumps(j, ensure_ascii=False, **kwargs)


def parse_xml(path):
    """
    >>> import filecmp
    >>> result = parse_xml("./tests/data/themes_90.xml")
    >>> with open("./tests/data/themes_90.txt.tmp", "w") as f:
    ...     for line in result:
    ...         _ = f.write(line.to_json() + "\\n")
    >>> filecmp.cmp("./tests/data/themes_90.txt", "./tests/data/themes_90.txt.tmp")
    True
    """

    with open(path, "rb") as f:
        xml = f.read()

    with open("titles.json", "rb") as f:
        titles = json.load(f)

    result = []
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
    """
    >>> convert_date("2007-09-04 19:30:45")
    '2007-09-04T19:30:45Z'
    """

    d = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    return d.isoformat() + "Z"


def group_comments(comments):
    """Группирует список комментариев в dict, где ключ - id комментария (может повторяться у
    дублирующихся комментариев), а значение - список дублирующихся комментариев:

    {
        "comment id": [Comment, Comment, ...],
        ...,
    }

    >>> import json
    >>> comments = parse_xml("./tests/data/themes_90.xml")
    >>> grouped = group_comments(comments)
    >>> grouped_dict = grouped.to_dict()
    >>> with open("./tests/data/grouped_themes_90.json", "rb") as f:
    ...     expected_dict = json.load(f)
    >>> grouped_dict == expected_dict
    True
    """

    gc = GroupedComments(comments)
    return gc


def filter_doubles(groups, comments):
    """На id комментария-дубля могут быть ответы и надо давить дупликаты с учетом этого.

    Убираем те комментарии-дубли, на id которых не ссылаются никакие другие комментарии.

    Модифицирует groups.
    """

    for id_, group in groups.items():
        # один комментарий, пропускаем
        if len(group) == 1:
            continue

        # больше одного комментария с одинаковым id
        filtered_group = []

        # оставляем комментарии, на которые ссылаются из других комментариев
        for g in group:
            for c in comments:
                if g._comment["id"] == c._comment["pid"]:
                    filtered_group.append(g)
                    break

        # for g in filtered_group:
        #     if "честное слово, у этой темы 0% попасть" in g._comment["text"]:
        #         print("DEBUG:", g.to_json())

        # если мы отфильтровали вообще все записи, то добавим в результат комментарий, который
        # является ответом на другой комментарий
        if not filtered_group:
            for g in group:
                if g._comment["pid"]:
                    filtered_group.append(g)
                    break

        # если мы отфильтровали вообще все записи, то добавим в результат любой из комментариев
        # дублей (например, первый)
        if not filtered_group:
            filtered_group = [group[0]]

        groups[id_] = filtered_group


def main():
    args = parse_args()
    result = parse_xml(args.INPUT)

    comments = parse_xml("./tests/data/themes_90.xml")
    grouped = group_comments(comments)
    print(grouped.to_json(indent=2))
    return
    # for group in grouped.values():
    #     print("---")
    #     print("LEN:", len(group))
    #     print("TEXT:", group[0]._comment["text"])
    # return

    if args.filter_doubles:
        groups = group_comments(result)
        filter_doubles(groups, result)
        for i in groups.values():
            for ii in i:
                print(ii.to_json())
        return

    if args.print_empty_urls:
        for i in result:
            if i.is_unknown_url():
                print(i[0].to_json())
        return

    for i in result:
        print(i.to_json())


if __name__ == "__main__":
    main()

