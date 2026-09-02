#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CGI script that reads news items from the SQLite database and outputs them as HTML."""

import argparse
import logging
import os
import sqlite3
import sys

DEFAULT_DB_PATH = "/usr/local/sisis-pap/wwwdir/cgi-bin/news.sqlite"
DEFAULT_LIMIT = 3
DEFAULT_KAT = "News"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db", default=os.environ.get("SCRAPER_DB_PATH", DEFAULT_DB_PATH),
        help="Path to the SQLite database (env: SCRAPER_DB_PATH)",
    )
    parser.add_argument(
        "--limit", type=int,
        default=int(os.environ.get("OPACNEWS_LIMIT", DEFAULT_LIMIT)),
        help="Maximum number of news items to display (env: OPACNEWS_LIMIT)",
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


def read_news(db_path, kat, limit):
    """Read news items from the database filtered by category."""
    with sqlite3.connect(db_path) as conn:
        conn.text_factory = str
        cursor = conn.execute(
            "SELECT * FROM news WHERE kat = ? LIMIT ?", (kat, limit)
        )
        return cursor.fetchall()


def render_html(items):
    """Render news items as HTML divs, each wrapped in a link."""
    parts = []
    for item in items:
        link = str(item[1])
        title = str(item[2])
        image = str(item[5])
        content = title + "\n" + image + "<br>\n"
        if link:
            content = '<a href="' + link + '">' + content + '</a>'
        parts.append('<div id="column" align="center">' + content + "</div>")
    return "\n".join(parts)


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.no_header:
        print("Content-Type: text/html;charset=utf-8")
        print()

    items = read_news(args.db, args.kat, args.limit)
    log.debug("Read %d news items from %s", len(items), args.db)

    print(render_html(items))


if __name__ == "__main__":
    main()
