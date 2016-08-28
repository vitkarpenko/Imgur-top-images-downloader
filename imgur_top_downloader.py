#!/usr/bin/env python3
"""Downloads up to 50 top results of Imgur search sorted by highest scoring.

Usage:
imgur_top_downloader cats
imgur_top_downloader "dwarf fortress"
"""
import logging
import argparse
import requests
import os
import multiprocessing
import shutil
import time
from collections import deque
from bs4 import BeautifulSoup


def download_image(link, directory):
    """Downloads image from link to directory.
    """
    r = requests.get(link)
    if r.status_code == 200:
        path = os.path.join(directory, os.path.basename(link))
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        logging.debug("Image from {} downloaded successfully.".format(link))
    else:
        logging.warning("Image from {} can't be downloaded.\n"
                        "Error code: {}.".format(link, r.status_code))


def get_gallery_links(search_value):
    """Gets the html of a search query on Imgur, parses it,
    and returns a deque of up to 50 links to gallery pages.
    """
    links = deque(maxlen=50)
    if ' ' not in search_value:
        search_query = "https://imgur.com/search?q={}".format(search_value)
    else:
        pluses_joined_search_value = '+'.join(search_value.split())
        search_query = "https://imgur.com/search?q={}".format(pluses_joined_search_value)
    r = requests.get(search_query)
    logging.debug("Search query: {}".format(search_query))
    soup = BeautifulSoup(r.text, "lxml")
    for element in soup.find_all("a", class_="image-list-link"):
        gallery_link = "https://imgur.com" + element.get('href')
        logging.debug("Gallery link: {}.".format("https://imgur.com" + element.get('href')))
        links.append(gallery_link)
    return links


def get_media_link(gallery_link):
    """Gets media link by gallery link.
    """
    r = requests.get(gallery_link)
    soup = BeautifulSoup(r.text, "lxml")
    # If image link is not present try to find video.
    try:
        media_link = soup.select('div.post-image img')[0].get('src')
    except IndexError:
        media_link = soup.select('div.post-image source')[0].get('src')
    logging.debug("Media link: {}.".format(media_link))
    return 'http:' + media_link


def main():
    """Main function.
    """
    # Start time.
    ts = time.time()

    # Setting up parser.
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

    # Setting up images folder.
    images_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                    'images')
    if not os.path.exists(images_directory):
        os.mkdir(images_directory)

    # Setting up images subdirectory.
    # If a directory with such name already exists it will be ruthlessly cleared.
    images_subdirectory = os.path.join(images_directory, search_value)
    if os.path.exists(images_subdirectory):
        shutil.rmtree(images_subdirectory, ignore_errors=True)
    os.mkdir(images_subdirectory)

    logging.info("Downloading '{}' images from Imgur.".format(args.search_value))

    # Collecting gallery links.
    gallery_links = get_gallery_links(args.search_value)

    # Collecting media links.
    pool_size = multiprocessing.cpu_count() * 2
    media_pool = multiprocessing.Pool(processes=pool_size)
    media_pool_output = media_pool.map(get_media_link, gallery_links)
    media_pool.close()
    media_pool.join()

    # Downloading links.
    logging.info("{} images to download.".format(len(media_pool_output)))
    pool = multiprocessing.Pool(processes=pool_size)
    pool.starmap(download_image, [(link, images_subdirectory) for link in media_pool_output])
    pool.close()
    pool.join()
    logging.info("Download finished successfully in {:.2f} seconds.".format(time.time() - ts))

if __name__ == '__main__':
    main()
