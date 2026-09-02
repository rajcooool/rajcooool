#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scrape news articles from stadtbibliothek-chemnitz.de and store them in a SQLite database."""

import argparse
import logging
import os
import sqlite3
import sys
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
import requests

BASE_URL = "https://www.stadtbibliothek-chemnitz.de"
DEFAULT_DB_PATH = "/usr/local/sisis-pap/wwwdir/cgi-bin/news.sqlite"
DEFAULT_PROXY = "http://proxy:3128"
DEFAULT_LIMIT = 5
REQUEST_TIMEOUT = 30
THUMBNAIL_WIDTH = 200
IMG_DISPLAY_WIDTH = 160

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
        "--proxy", default=os.environ.get("SCRAPER_PROXY", DEFAULT_PROXY),
        help="HTTP(S) proxy URL (env: SCRAPER_PROXY, empty string to disable)",
    )
    parser.add_argument(
        "--limit", type=int,
        default=int(os.environ.get("SCRAPER_LIMIT", DEFAULT_LIMIT)),
        help="Maximum number of news items to process (env: SCRAPER_LIMIT)",
    )
    parser.add_argument(
        "--url", default=os.environ.get("SCRAPER_URL", BASE_URL + "/"),
        help="URL to scrape (env: SCRAPER_URL)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


def make_absolute(url: str) -> str:
    """Convert a relative URL to an absolute one using BASE_URL."""
    if url.startswith("http"):
        return url
    return urljoin(BASE_URL, url)


def extract_image(element: Tag) -> str:
    """Extract a thumbnail image tag from a news block element."""
    img_tag = element.find("img")
    if img_tag and img_tag.get("data-img-uri"):
        src = img_tag["data-img-uri"] + f"&w={THUMBNAIL_WIDTH}"
        return f'<img src="{src}" width="{IMG_DISPLAY_WIDTH}">'

    noscript = element.find("noscript")
    if noscript:
        fallback_img = noscript.find("img")
        if fallback_img:
            fallback_img["src"] = make_absolute(fallback_img.get("src", ""))
            fallback_img["width"] = str(IMG_DISPLAY_WIDTH)
            if fallback_img.has_attr("height"):
                del fallback_img["height"]
            return str(fallback_img)

    return ""


def extract_link(element: Tag) -> str:
    """Extract the 'mehr' link from a news block and make it absolute."""
    link_div = element.find("div", class_="cc_links")
    if link_div:
        a_tag = link_div.find("a")
        if a_tag:
            a_tag["href"] = make_absolute(a_tag.get("href", ""))
            return str(a_tag)
    return ""


def fetch_page(url: str, proxies: dict) -> str:
    """Fetch a page and return its HTML content."""
    response = requests.get(url, proxies=proxies, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.text


def scrape_news(html: str, limit: int) -> list[dict]:
    """Parse news blocks from HTML and return a list of extracted items."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    for element in soup.find_all("div", class_="cc_content_block cc_news_block"):
        title = str(element.h3) if element.h3 else ""

        date_div = element.find("div", class_="cc_news_info")
        date = date_div.get_text(strip=True) if date_div else ""

        image = extract_image(element)
        link = extract_link(element)

        items.append({"title": title, "date": date, "image": image, "link": link})

        if len(items) >= limit:
            break

    return items


def store_news(db_path: str, items: list[dict]):
    """Write scraped news items into the SQLite database."""
    with sqlite3.connect(db_path) as conn:
        conn.text_factory = str
        for count, item in enumerate(items, start=1):
            conn.execute(
                "UPDATE news SET link=?, title=?, kat=?, image=? WHERE ID=?",
                (item["link"], item["title"], "News", item["image"], count),
            )
        conn.commit()
    log.info("Stored %d news items in %s", len(items), db_path)


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    proxies = {}
    if args.proxy:
        proxies = {"http": args.proxy, "https": args.proxy}

    log.info("Fetching %s", args.url)
    html = fetch_page(args.url, proxies)

    items = scrape_news(html, args.limit)
    log.info("Extracted %d news items", len(items))

    for item in items:
        log.debug("Title: %s | Date: %s", item["title"], item["date"])

    store_news(args.db, items)


if __name__ == "__main__":
    main()
