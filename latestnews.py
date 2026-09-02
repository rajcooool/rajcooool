#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CGI script that displays a random news item or a static OPAC App teaser."""

import argparse
import logging
import os
import sqlite3
import sys
from random import randint

DEFAULT_DB_PATH = "/usr/local/sisis-pap/wwwdir/cgi-bin/news.sqlite"
DEFAULT_KAT = "News"
DEFAULT_MAX_RANDOM = 6

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

OPAC_APP_HTML = (
    '<ul><li><h3>OPAC App</br>für Android und IOS</h3>'
    '<a href="https://www.stadtbibliothek-chemnitz.de/bibliothek-service/service/opac-app"'
    ' title="OPAC App für Android und IOS" class="text">'
    '<img alt="" border="0" height="87"'
    ' src="https://opac2.stadtbibliothek-chemnitz.de/opacapp.png"'
    ' class="imgcenter" title="OPAC App für Android und IOS"/>'
    '</a></li></ul>'
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db", default=os.environ.get("SCRAPER_DB_PATH", DEFAULT_DB_PATH),
        help="Path to the SQLite database (env: SCRAPER_DB_PATH)",
    )
    parser.add_argument(
        "--kat", default=os.environ.get("OPACNEWS_KAT", DEFAULT_KAT),
        help="Category to filter by (env: OPACNEWS_KAT)",
    )
    parser.add_argument(
        "--no-header", action="store_true",
        help="Omit the CGI Content-Type header (for non-CGI usage)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


def read_news(db_path, kat):
    """Read all news items for the given category."""
    with sqlite3.connect(db_path) as conn:
        conn.text_factory = str
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT link, title, image FROM news WHERE kat = ?", (kat,)
        )
        return cursor.fetchall()


def render_news_item(item):
    """Render a single news item as HTML with the link wrapping the entire content."""
    link = item["link"]
    title = item["title"]
    image = item["image"].replace("&w=200", "&w=150")
    content = title + "\n" + image + "<br>\n"
    if link:
        content = '<a href="' + link + '">' + content + '</a>'
    return '<div id="column" align="center">' + content + "</div>"


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.no_header:
        print("Content-Type: text/html;charset=utf-8")
        print()

    treffer = randint(1, DEFAULT_MAX_RANDOM)
    log.debug("Random pick: %d", treffer)

    print("<div id='cssmenu'>")

    if treffer < DEFAULT_MAX_RANDOM:
        items = read_news(args.db, args.kat)
        if treffer <= len(items):
            print(render_news_item(items[treffer - 1]))
    else:
        print(OPAC_APP_HTML)

    print("</div>")


if __name__ == "__main__":
    main()
