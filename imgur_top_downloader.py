#!/usr/bin/env python3
"""Downloads up to 50 top results of Imgur search sorted by highest scoring.

Usage:
imgur_top_downloader cats
imgur_top_downloader "dwarf fortress"
"""
import logging
import argparse
import requests
import multiprocessing
from bs4 import BeautifulSoup


def download_image(link, directory):
    """Downloads image from link to directory.
    """
    logging.debug("Downloading image from {}.".format(link))
    r = requests.get(link)
    if r.status_code == 200:
        path = os.path.join(directory, os.path.basename(link))
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        logging.debug("Image downloaded successfully.")
    else:
        logging.debug("Image can't be downloaded. Error code: {}.".format(r.status_code))


def get_image_links(search_value):
    """Gets the html of a search query on Imgur, parses it,
    and returns a list of up to 50 links to pictures.
    """
    r = requests.get("https://imgur.com/search?q={}".format(search_value))
    logging.debug("Search query: https://imgur.com/search?q={}".format(search_value))
    soup = BeautifulSoup(r.text, "lxml")
    for element in soup.find_all("a", class_="image-list-link"):
        gallery_link = "https://imgur.com" + element.get('href')
        logging.debug("Gallery link: {}.".format("https://imgur.com" + element.get('href')))


def main():
    """Main function.
    """
    parser = argparse.ArgumentParser(description="Downloads up to 50 top results of Imgur search"
                                                 "sorted by highest scoring.")
    parser.add_argument(
        'search_value',
        help="The word for which you want to search.")
    parser.add_argument(
        '-d', '--debug',
        help="Print debugging statements.",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.INFO)

    # Processing arguments.
    args = parser.parse_args()
    search_value = args.search_value

    # Setting up logger.
    logging.basicConfig(level=args.loglevel, format='%(levelname)s: %(message)s')
    logging.getLogger("requests").setLevel(logging.WARNING)

    logging.info("Downloading {} images from Imgur.".format(args.search_value))
    get_image_links(args.search_value)


if __name__ == '__main__':
    main()
