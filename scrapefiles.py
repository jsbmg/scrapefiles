#! /usr/bin/env python3

"""
Downloads files linked on a webpage that match a given regex.

Requires: 
    Python3.6+
"""

import argparse
import os
import re
import sys

from html.parser import HTMLParser
from shutil import copyfileobj
from urllib.request import urlopen


class LinkGrabber(HTMLParser):

    def __init__(self, url):
        HTMLParser.__init__(self)
        self.links = list()
        r = urlopen(url)
        self.feed(r.read().decode("utf-8"))

    def handle_starttag(self, tag, attrs):
        links = []
        if tag == 'a' and attrs:
            self.links.append(attrs)

            
def find_matching_links(url, match) -> list:
    """Return a list of links in a url that match a regex."""
    links = LinkGrabber(url)
    regex = re.compile(match)
    all_links = [link[0][1] for link in links.links]
    matched_links = list(filter(regex.match, all_links))
    return matched_links


def download_file(link, destination):
    """Download a file from a url."""
    file_name = link.split('/')[-1]
    destination = os.path.join(destination, file_name)
    print(f"Downloading: {destination}")

    with urlopen(link) as response, open(destination, 'wb') as out_file:
        copyfileobj(response, out_file)

def download_all(links, destination):
    """Download all files from a list of urls."""
    for link in links:
        download_file(link, destination)

def main():
    parser = argparse.ArgumentParser(description='Download files from a webpage.')
    parser.add_argument('url', help='the url that contains the links')
    parser.add_argument('--dir', help='specify the download directory')
    parser.add_argument('--match',
                        help='the regex to filter by',
                        required=True)
    parser.add_argument('-y', action='store_true',
                        help='download without confirmation')
    args = parser.parse_args()
    
    links = find_matching_links(args.url, args.match)
    num_links = len(links)
        
    if num_links == 0:
        print(f"No matching links found.")
        return 3
    
    if args.dir:
        destination = args.dir
    else:
        destination = os.getcwd()
    
    if args.y:
        download_all(links, destination)
        return 0
    else:
        for idx in range(min(5, num_links)):
            print(links[idx].split('/')[-1])
        print(f"...\n{num_links} file(s) found. Download to {destination}? (yes|no) [yes]")
        links_correct = input("> ")
        if links_correct == "yes" or links_correct == "":
            download_all(links, destination)
            return 0
        return 3

        
if __name__ == "__main__":
    sys.exit(main())

