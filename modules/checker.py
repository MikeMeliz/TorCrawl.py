#!/usr/bin/python

import os
import re
import subprocess
import sys
from json import load
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlopen


def url_canon(website, verbose):
    """ URL normalisation/canonicalization

    :param website: String - URL of website.
    :param verbose: Boolean - Verbose logging switch.
    :return: String 'website' - normalised result.
    """
    if not website.startswith("http"):
        if not website.startswith("www."):
            website = "www." + website
            if verbose:
                print(("## URL fixed: " + website))
        website = "http://" + website
        if verbose:
            print(("## URL fixed: " + website))
    return website


def extract_domain(url, remove_http=True):
    """ Parses the provided 'url' to provide only the netloc or
    scheme + netloc parts of the provided url.

    :param url: String - Url to parse.
    :param remove_http: Boolean
    :return: String 'domain_name' - Resulting parsed Url
    """
    uri = urlparse(url)
    if remove_http:
        domain_name = f"{uri.netloc}"
    else:
        domain_name = f"{uri.scheme}://{uri.netloc}"
    return domain_name


# Create output path
def folder(website, verbose):
    """ Creates an output path for the findings.

    :param website: String - URL of website to crawl.
    :param verbose: Boolean - Logging level.
    :return: String 'out_path' - Path of the output folder.
    """
    out_path = website
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    if verbose:
        print(f"## Folder created: {out_path}")
    return out_path


def check_tor(verbose):
    """Checks to see if TOR service is running on device.
    Will exit if (-w) with argument is provided on application startup and TOR
    service is not found to be running on the device.

    :param verbose: Boolean -'verbose' logging argument.
    :return: None
    """
    check_for_tor = subprocess.check_output(['ps', '-e'])

    def find_whole_word(word):
        return re.compile(r'\b({0})\b'.format(word),
                          flags=re.IGNORECASE).search

    if find_whole_word('tor')(str(check_for_tor)):
        if verbose:
            print("## TOR is ready!")
    else:
        print("## TOR is NOT running!")
        print('## Enable tor with \'service tor start\' or add -w argument')
        sys.exit(2)


def check_ip():
    """ Checks users IP from external resource.
    :return: None or HTTPError
    """
    addr = 'https://api.ipify.org/?format=json'
    try:
        my_ip = load(urlopen(addr))['ip']
        print(f'## Your IP: {my_ip}')
    except HTTPError as err:
        error = sys.exc_info()[0]
        print(f"Error: {error} \n## IP cannot be obtained. \n## Is {addr} up? "
              f"\n## HTTPError: {err}")
