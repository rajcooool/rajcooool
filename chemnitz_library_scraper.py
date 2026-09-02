#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys

from bs4 import BeautifulSoup
import requests
import re

proxies = {
  'http': 'http://proxy:3128',
  'https': 'http://proxy:3128',
}

BASE_URL = "https://www.stadtbibliothek-chemnitz.de"

limit = 5
conn = sqlite3.connect('/usr/local/sisis-pap/wwwdir/cgi-bin/news.sqlite')
conn.text_factory = str

r = requests.get(BASE_URL + "/", proxies=proxies)

data = r.text

soup = BeautifulSoup(data, "lxml")

count = 1

for element in soup.find_all("div", class_="cc_content_block cc_news_block"):
      title = str(element.h3)

      # Date is now inside each news block
      date_div = element.find("div", class_="cc_news_info")
      date = str(date_div) if date_div else ""

      # Image: src is already an absolute URL, use data-img-uri with &w=200 for thumbnail
      img_tag = element.find("img")
      if img_tag and img_tag.get("data-img-uri"):
          image = '<img src="' + img_tag["data-img-uri"] + '&w=200" width="160">'
      else:
          # Fallback to noscript image
          noscript = element.find("noscript")
          if noscript:
              image = str(noscript)
              image = image.replace('src="/', 'src="' + BASE_URL + '/')
              image = image.replace('<noscript>', '')
              image = image.replace('</noscript>', '')
              image = re.sub(r'height="\d+"', '', image)
              image = re.sub(r'width="\d+"', 'width="160"', image)
          else:
              image = ""

      # Link is now in div.cc_links
      link_div = element.find("div", class_="cc_links")
      if link_div and link_div.a:
          link = str(link_div.a)
          link = link.replace('href="/', 'href="' + BASE_URL + '/')
      else:
          link = ""

      print(link, "\n")
      print(title, "\n")
      print(image, "\n")
      print(date, "\n")

      conn.execute("UPDATE news SET link=?,title=?,kat=?,image=? WHERE ID=?", (link, title, "News", image, count))

      if limit == count:
         break

      count += 1

conn.commit()
conn.close()
