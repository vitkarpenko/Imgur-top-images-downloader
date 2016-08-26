#!/usr/bin/env python3
"""Downloads up to 50 top results of Imgur search sorted by highest scoring.

Usage:
imgur_top_downloader cats
imgur_top_downloader "dwarf fortress"
"""
import logging
import argparse


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

args = parser.parse_args()

logging.basicConfig(level=args.loglevel)
