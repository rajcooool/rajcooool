#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
#import cgitb
#cgitb.enable()

from bs4 import BeautifulSoup
from random import randint
import requests
import string
import re

proxies = {
  'http': 'http://proxy:3128',
  'https': 'http://proxy:3128',
}

limit = 5
conn = sqlite3.connect('/usr/local/sisis-pap/wwwdir/cgi-bin/news.sqlite')
conn.text_factory = str

r  = requests.get("https://www.stadtbibliothek-chemnitz.de/", proxies=proxies)
# r  = requests.get("https://www.stadtbibliothek-chemnitz.de/aktuelles/news", proxies=proxies)

data = r.text

soup = BeautifulSoup(data, "lxml")

count = 1

for element in soup.find_all("div", class_="cc_content_block cc_news_block"):
      # print element, "\n\n"
      title = str(element.h3)
      title = title.replace('href=\"', 'href=\"https://www.stadtbibliothek-chemnitz.de')
      #title = re.sub(r" title=", " class=\"text\"  onClick=\"ga('send', 'event', 'Pointer', 'Click', 'Medientipps');\" title=", title)
      image = str(element.figure.noscript)
      image2 = str(element.img)
      image2 = re.sub('^.*data-img-uri=\"(.*?)\" .*', '<img src=\"https://www.stadtbibliothek-chemnitz.de'r'\1''&w=200\">', str(element))
      #image2 = re.sub('^.*data-img-uri=\"(.*?)\" .*', '<img src=\"https://www.stadtbibliothek-chemnitz.de'r'\1''&w=200\ style=\"max-height: 200px;\">', str(element))
      image = image.replace('src=\"', 'src=\"https://www.stadtbibliothek-chemnitz.de')
      image = image.replace('<noscript>', '')
      image = image.replace('</noscript>', '')
      image = re.sub('height=\"\d+\"', '', image)
      image = re.sub('width=\"\d+\"', 'width=\"160\"', image)
      # image = image.replace('width=\".*\"', 'width=\"200\"')
      link = str(element.a)
      print(link, "\n")
      link = link.replace('href=\"/', 'href=\"https://www.stadtbibliothek-chemnitz.de/')
      # link = link.replace('href=\"', 'href=\"https://')
      for date in soup.find_all("div", class_="cc_news_info"):
         date = str(date)
      #link = link.replace('href=\"', 'href=\"https://www.stadtbibliothek-chemnitz.de')
      #link = re.sub(r"><i", " class=\"text\"  onClick=\"ga('send', 'event', 'Pointer', 'Click', 'Medientipps');\"><i", link)
      #link = link.replace('src=\"', 'src=\"https://www.stadtbibliothek-chemnitz.de')
      #print "<a href=\"https://www.stadtbibliothek-chemnitz.de/aktuell/medientipps.html\" target=\"_blank\"><span>Tipps</span></a>"
      #image = str(element.img)
      #image = image.replace('data-img-uri=\"/', 'data-img-uri=\"https://www.stadtbibliothek-chemnitz.de')
      # image = image.replace('src=\"data:image/', 'src=\"data:image\"https://www.stadtbibliothek-chemnitz.de')
      print(link, "\n")
      print(title, "\n")
      print(image, "\n")
      print(date, "\n")
      #print str(count) + "\n"
      print(image2, "\n\n")

      print(element, "\n")
      conn.execute("UPDATE news SET link=?,title=?,kat=?,image=? WHERE ID=?", (link,title,"News",image,count))

      if limit == count:
         break

      count += 1

#count = 4
#for element in soup.find_all("div", class_="news-latest-item"):
      #print treffer
      #title = str(element.h3)
      #title = title.replace('href=\"', 'href=\"http://www.stadtbibliothek-chemnitz.de/')
      #title = re.sub(r" title=", " class=\"text\" onClick=\"ga('send', 'event', 'Pointer', 'Click', 'Veranstaltungen');\" title=", title)
      #link = str(element.a)
      #link = link.replace('href=\"', 'href=\"http://www.stadtbibliothek-chemnitz.de/')
      #link = re.sub(r"><i", " class=\"text\" onClick=\"ga('send', 'event', 'Pointer', 'Click', 'Veranstaltungen');\"><i", link)
      #link = link.replace('src=\"', 'src=\"http://www.stadtbibliothek-chemnitz.de/')
      #print "<a href=\"http://www.stadtbibliothek-chemnitz.de/aktuell/newsblog.html\" target=\"_blank\"><span>News</span></a>"
      #print link
      #print title
      #text = str(element.p)
      #print str(count) + "\n"

      # conn.execute("UPDATE news SET link=?,title=?,text=?,kat=? WHERE ID=?", (link,title,text,"Veranstaltungen",count))
      #count += 1

conn.commit()
conn.close()
