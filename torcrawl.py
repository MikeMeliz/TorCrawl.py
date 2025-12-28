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
-v, --verbose      : Show more information about the progress
-u, --url *.onion  : URL of Webpage to crawl or extract
-w, --without      : Without the use of Relay TOR
-rua, --random-ua  : Enable random user-agent rotation for requests
-rpr, --random-proxy: Enable random proxy rotation from res/proxies.txt

Extract:
-e, --extract           : Extract page's code to terminal or file.
                          (Default: terminal)
-i, --input filename    : Input file with URL(s) (separated by line)
-o, --output [filename] : Output page(s) to file(s) (for one page)
-y, --yara              : Yara keyword search page categorisation
                            read in from /res folder. 
                            'h' search whole html object.
                            't' search only the text.

Crawl:
-c, --crawl       : Crawl website (Default output on /links.txt)
-d, --depth      : Set depth of crawl's travel (Default: 1)
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
import datetime

import socks  # noqa - pysocks

from modules.checker import check_ip
from modules.checker import check_tor
from modules.checker import extract_domain
from modules.checker import folder
from modules.checker import url_canon
# TorCrawl Modules
from modules.crawler import Crawler
from modules.extractor import extractor

__version__ = "1.34"


# Set socket and connection with TOR network
def connect_tor(proxy_url, proxy_port):
    """ Connect to TOR via DNS resolution through a socket.
    :return: None or HTTPError.
    """
    try:
        # Set socks proxy and wrap the urllib module
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_url, proxy_port)
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
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version=f"%(prog)s {__version__}"
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
        help='Input file with URL(s) (separated by line)'
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
        '--depth',
        help='Set depth of crawl\'s travel (Default: 1)'
    )
    parser.add_argument(
        '-p',
        '--pause',
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
        help='Check for keywords and only scrape documents that contain a '
             'match. \'h\' search whole html object. \'t\' search only the text.'
    )
    parser.add_argument(
        '-rua',
        '--random-ua',
        action='store_true',
        help='Enable random user-agent rotation for requests'
    )
    parser.add_argument(
        '-rpr',
        '--random-proxy',
        action='store_true',
        help='Enable random proxy rotation from res/proxies.txt'
    )
    parser.add_argument(
        '-pr',
        '--proxyport',
        help='Port for SOCKS5 proxy',default=9050
    )
    parser.add_argument(
        '-px',
        '--proxy',
        help='IP address for SOCKS5 proxy',default='127.0.0.1'
    )

    args = parser.parse_args()

    now = datetime.datetime.now().strftime("%y%m%d")

    # Canonicalization of web url and create path for output.
    website = ''
    output_folder = ''

    if args.input: pass
    elif len(args.url) > 0:
        website = url_canon(args.url, args.verbose)
        if args.folder is not None:
            output_folder = folder(args.folder, args.verbose)
        else:
            output_folder = folder(extract_domain(website), args.verbose)

    # Parse arguments to variables else initiate variables.
    input_file = args.input if args.input else ''
    output_file = args.output if args.output else ''
    depth = args.depth if args.depth else 0
    pause = args.pause if args.pause else 0
    selection_yara = args.yara if args.yara else None
    random_ua = args.random_ua
    random_proxy = args.random_proxy

    # Random proxy rotation only works when TOR is disabled
    if random_proxy and args.without is False:
        print("## Warning: Random proxy rotation requires --without (-w) flag to disable TOR.")
        print("## Random proxy rotation disabled. Using TOR instead.")
        random_proxy = False

    # Connect to TOR or random proxy
    if random_proxy:
        # Random proxy rotation enabled - will be handled per request
        if args.verbose:
            print("## Random proxy rotation enabled (TOR disabled)")
    elif args.without is False:
        check_tor(args.verbose)
        connect_tor(args.proxy, args.proxyport)

    if args.verbose:
        check_ip()
        if args.url: print(('## URL: ' + args.url))

    if args.crawl:
        crawler = Crawler(website, depth, pause, output_folder, args.log,
                          args.verbose, random_ua, random_proxy)
        lst = crawler.crawl()

        if args.input is None:
            input_file = output_folder + '/' + now + '_links.txt'
      
        with open(input_file, 'w+', encoding='UTF-8') as file:
            for item in lst:
                file.write(f"{item}\n")
        print(f"## File created on {os.getcwd()}/{input_file}")

        if args.extract:
            extractor(website, args.crawl, output_file, input_file, output_folder,
                      selection_yara, random_ua, random_proxy)
    else:
        extractor(website, args.crawl, output_file, input_file, output_folder,
                  selection_yara, random_ua, random_proxy)


# Stub to call main method.
if __name__ == "__main__":
    main()
