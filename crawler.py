#!/usr/bin/env python3

import anyio
import re
import requests
import requests_cache
from bs4 import BeautifulSoup
from decouple import config
from tinydb import TinyDB, Query
from urllib.parse import urljoin
from tinydb import TinyDB, Query

#  env vars
name = config("NAME", default="goodreads")
url = config("URL", default="https://www.goodreads.com/quotes")
ttl = config("TTL", default=300)

# database
db = TinyDB("db.json")

# cache the requests to sqlite, expire after n time
if not ttl:
    min = 5
    sec = 60
    ttl = min * sec

# client
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0"
}
client = requests_cache.CachedSession(cache_name=name,
                                      backend="sqlite",
                                      expire_after=ttl
)


def get_html(url, cursor=None):
    """Return the html from the url."""

    res = client.get(str(url), headers=headers)

    return res


def capture_data(html):
    """Capture the text from the specified div and span classes."""

    soup = BeautifulSoup(html, "html.parser")

    quotes_div = soup.find("div", class_="quotes")
    if quotes_div is not None:
        quote_texts = quotes_div.find_all("div", class_="quoteText")

        data = []

        for quote_text in quote_texts:
            quote = "".join(str(item) for item in quote_text.contents)
            quote = quote.split('<span class="authorOrTitle">')[0]
            author = quote_text.find("span", class_="authorOrTitle").text
            data.append({"quote": quote, "author": author})
    else:
        data = []

    return data


def strip_characters(data):
    """Strip characters from the data."""

    for item in data:
        for key, value in item.items():
            if key == "quote":
                value = re.sub(r"\u201c|\u201d|\u2015.*", "", value)
                value = value.split("\u2015")[0].strip()
                value = value.replace("\u2019", "'").replace("\u2026", "...")
                value = value.rstrip("\n")
                value = value.replace("<br>", "\n")
                value = value.replace("<br/>", "\n")
                item[key] = value.strip()
            elif key == "author":
                value = value.strip()
                item[key] = value

    return data


def sanitize_data(data):
    """Remove non-ascii characters from the data."""

    valid_data = {}

    for id, entry in enumerate(data):
        if isinstance(entry, dict):
            quote = entry.get('quote')
            author = entry.get('author')
            if quote and author and quote.isascii() and author.isascii():
                valid_data[id] = entry

    return valid_data


async def main():
    # ! drop the table (qa)
    # db.drop_tables()

    # initialize cursor with the starting URL
    cursor = url

    while cursor:
        # get the raw html
        res = get_html(cursor)

        # read the html
        html = res.text

        # capture the data
        data = capture_data(html)

        # strip characters
        data = strip_characters(data)

        # sanitize data
        data = sanitize_data(data)

        # convert data to a list of dictionaries
        data_list = [entry for entry in data.values()]

        # export to db.json
        db.insert_multiple(data_list)

        # check if there is a next page
        soup = BeautifulSoup(html, "html.parser")
        next_page_link = soup.find("a", rel="next")
        if next_page_link:
            cursor = urljoin(url, next_page_link["href"])
        else:
            cursor = None


if __name__ == "__main__":
    anyio.run(main)
