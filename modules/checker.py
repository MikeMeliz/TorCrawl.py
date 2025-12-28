#!/usr/bin/python

import os
import importlib.resources as resources
import random
import re
import socket
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
    if not website.startswith("http://") and not website.startswith("https://"):
        website = "https://" + website
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
    :return: String 'output_folder' - Path of the output folder.
    """
    # Ensure base output directory exists
    if not os.path.exists('output'):
        try:
            os.makedirs('output')
        except (OSError, PermissionError):
            pass  # Silently fail if can't create, will error later if needed
    
    parsed = urlparse(website)
    if parsed.scheme != '':
        output_folder = "output/" + urlparse(website).netloc
    else:
        output_folder = "output/" + website
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
        except FileExistsError:
            if verbose:
                print(f"## Folder exists already: {website}")
    if verbose:
        print(f"## Folder created: {website}")
    return output_folder


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
    api_address = 'https://api.ipify.org/?format=json'
    try:
        my_ip = load(urlopen(api_address))['ip']
        print(f'## Your IP: {my_ip}')
    except HTTPError as err:
        error = sys.exc_info()[0]
        print(f"Error: {error} \n## IP cannot be obtained. \n## Is {api_address} up? "
              f"\n## HTTPError: {err}")


_user_agents_cache = None
_proxies_cache = None


def _read_resource_file(filename):
    """Return absolute path to packaged resource, falling back to CWD."""
    try:
        return resources.files("res").joinpath(filename)
    except (FileNotFoundError, ModuleNotFoundError):
        # Fallback for non-installed executions
        return os.path.join("res", filename)


def get_random_user_agent():
    """ Loads user-agents from res/user_agents.txt and returns a random one.
    
    :return: String - Random user-agent string
    """
    global _user_agents_cache
    
    if _user_agents_cache is None:
        user_agents_file = _read_resource_file('user_agents.txt')
        try:
            with open(user_agents_file, 'r', encoding='UTF-8') as f:
                _user_agents_cache = [line.strip() for line in f if line.strip()]
        except IOError:
            print(f"## Warning: Could not load user-agents from {user_agents_file}")
            return None
    
    if _user_agents_cache:
        return random.choice(_user_agents_cache)
    return None


def get_random_proxy():
    """ Loads proxies from res/proxies.txt and returns a random one.
    If no proxies are found, displays a helpful message with instructions.
    
    :return: String - Random proxy string (format: host:port) or None if no proxies available
    """
    global _proxies_cache
    
    if _proxies_cache is None:
        proxies_file = _read_resource_file('proxies.txt')
        try:
            with open(proxies_file, 'r', encoding='UTF-8') as f:
                _proxies_cache = [line.strip() for line in f if line.strip()]
        except IOError:
            print(f"## Warning: Could not load proxies from {proxies_file}")
            return None
        
        # If no proxies found, show helpful message
        if not _proxies_cache:
            print("## No proxies found in res/proxies.txt")
            print("## Please add proxies to res/proxies.txt, one per line.")
            print("## Example format:")
            print("##   127.0.0.1:9050")
            print("##   192.168.1.1:8080")
            print("##   proxy.example.com:3128")
            return None
    
    if _proxies_cache:
        return random.choice(_proxies_cache)
    return None


def setup_proxy_connection(proxy_string):
    """ Sets up a SOCKS5 proxy connection for a request.
    
    :param proxy_string: String - Proxy in format "host:port"
    :return: None
    """
    try:
        import socks  # noqa - pysocks
    except ImportError:
        print("## Error: pysocks module is required for proxy rotation. Install it with: pip install pysocks")
        return
    
    try:
        if ':' not in proxy_string:
            print(f"## Warning: Invalid proxy format: {proxy_string}. Expected host:port")
            return
        
        proxy_host, proxy_port = proxy_string.split(':', 1)
        proxy_port = int(proxy_port)
        
        # Set socks proxy and wrap the urllib module
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_host, proxy_port)
        socket.socket = socks.socksocket
        
        # Perform DNS resolution through the socket
        def getaddrinfo(*args):  # noqa
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '',
                     (args[0], args[1]))]
        
        socket.getaddrinfo = getaddrinfo  # noqa
    except (ValueError, socks.HTTPError) as err:
        print(f"## Warning: Could not set up proxy {proxy_string}: {err}")
