#!/usr/bin/python
"""
TorCrawl.py is a python script to crawl and extract (regular or onion)
webpages through TOR network.

usage: python torcrawl.py [options]
python torcrawl.py -u l0r3m1p5umD0lorS1t4m3t.onion
python torcrawl.py -v -w -u http://www.github.com -o github.htm
python torcrawl.py -v -u l0r3m1p5umD0lorS1t4m3t.onion -c -d 2 -p 5
python torcrawl.py -v -w -u http://www.github.com -c -d 2 -p 5 -e -f GitHub

General:
-h, --help         : Help
-v, --verbose      : Show more informations about the progress
-u, --url *.onion  : URL of Webpage to crawl or extract
-w, --without      : Without the use of Relay TOR

Extract:
-e, --extract           : Extract page's code to terminal or file.
                          (Defualt: terminal)
-i, --input filename    : Input file with URL(s) (seperated by line)
-o, --output [filename] : Output page(s) to file(s) (for one page)

Crawl:
-c, --crawl       : Crawl website (Default output on /links.txt)
-d, --cdepth      : Set depth of crawl's travel (Default: 1)
-z, --exclusions  : Paths that you don't want to include (TODO)
-s, --simultaneous: How many pages to visit at the same time (TODO)
-p, --pause       : The length of time the crawler will pause
                    (Default: 0)
-f, --folder	  : The root directory which will contain the
                    generated files
-l, --log         : Log file with visited URLs and their response code.

GitHub: github.com/MikeMeliz/TorCrawl.py
License: GNU General Public License v3.0

"""

import argparse
import os
import socket
import sys

import socks  # noqa - pysocks

from modules.checker import check_ip
from modules.checker import check_tor
from modules.checker import extract_domain
from modules.checker import folder
from modules.checker import url_canon
# TorCrawl Modules
from modules.crawler import Crawler
from modules.extractor import extractor


# Set socket and connection with TOR network
def connect_tor():
    """ Connect to TOR via DNS resolution through a socket.
    :return: None or HTTPError.
    """
    try:
        port = 9050
        # Set socks proxy and wrap the urllib module
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', port)
        socket.socket = socks.socksocket

        # Perform DNS resolution through the socket
        def getaddrinfo(*args):  # noqa
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '',
                     (args[0], args[1]))]

        socket.getaddrinfo = getaddrinfo  # noqa
    except socks.HTTPError as err:
        error = sys.exc_info()[0]
        print(f"Error: {error} \n## Cannot establish connection with TOR\n"
              f"HTTPError: {err}")


def main():
    """ Main method of TorCrawl application. Collects and parses arguments and
    instructs the rest of the application on how to run.

    :return: None
    """

    # Get arguments with argparse.
    parser = argparse.ArgumentParser(
        description="TorCrawl.py is a python script to crawl and extract "
                    "(regular or onion) webpages through TOR network.")

    # General
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Show more information about the progress'
    )
    parser.add_argument(
        '-u',
        '--url',
        help='URL of webpage to crawl or extract'
    )
    parser.add_argument(
        '-w',
        '--without',
        action='store_true',
        help='Without the use of Relay TOR'
    )

    # Extract
    parser.add_argument(
        '-e',
        '--extract',
        action='store_true',
        help='Extract page\'s code to terminal or file.'
    )
    parser.add_argument(
        '-i',
        '--input',
        help='Input file with URL(s) (seperated by line)'
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Output page(s) to file(s) (for one page)'
    )

    # Crawl
    parser.add_argument(
        '-c',
        '--crawl',
        action='store_true',
        help='Crawl website (Default output on /links.txt)'
    )
    parser.add_argument(
        '-d',
        '--cdepth',
        help='Set depth of crawl\'s travel (Default: 1)'
    )
    parser.add_argument(
        '-p',
        '--cpause',
        help='The length of time the crawler will pause'
    )
    parser.add_argument(
        '-l',
        '--log',
        action='store_true',
        help='A save log will let you see which URLs were visited and their '
             'response code'
    )
    parser.add_argument(
        '-f',
        '--folder',
        help='The root directory which will contain the generated files'
    )
    parser.add_argument(
        '-y',
        '--yara',
        action='store_true',
        help='Check for keywords and only scrape documents that contain a '
             'match.'
    )

    args = parser.parse_args()

    # Parse arguments to variables else initiate variables.
    input_file = args.input if args.input else ''
    output_file = args.output if args.output else ''
    c_depth = args.cdepth if args.cdepth else 0
    c_pause = args.cpause if args.cpause else 1

    # Connect to TOR
    if args.without is False:
        check_tor(args.verbose)
        connect_tor()

    if args.verbose:
        check_ip()
        print(('## URL: ' + args.url))

    website = ''
    out_path = ''

    # Canon/ion of website and create path for output
    if len(args.url) > 0:
        website = url_canon(args.url, args.verbose)
        if args.folder is not None:
            out_path = folder(args.folder, args.verbose)
        else:
            out_path = folder(extract_domain(website), args.verbose)

    if args.crawl:
        crawler = Crawler(website, c_depth, c_pause, out_path, args.log,
                          args.verbose)
        lst = crawler.crawl()
        with open(out_path + '/links.txt', 'w+', encoding='UTF-8') as file:
            for item in lst:
                file.write(f"{item}\n")
        print(f"## File created on {os.getcwd()}/{out_path}/links.txt")
        if args.extract:
            input_file = out_path + "/links.txt"
            extractor(website, args.crawl, output_file, input_file, out_path,
                      args.yara)
    else:
        extractor(website, args.crawl, output_file, input_file, out_path,
                  args.yara)


# Stub to call main method.
if __name__ == "__main__":
    main()
