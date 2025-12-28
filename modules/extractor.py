#!/usr/bin/python
import io
import os
import importlib.resources as resources
import urllib.error
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError
from http.client import InvalidURL
from http.client import IncompleteRead
from bs4 import BeautifulSoup
from pathlib import Path

from modules.checker import url_canon
from modules.checker import get_random_user_agent
from modules.checker import get_random_proxy
from modules.checker import setup_proxy_connection


def text(response=None):
    """ Removes all the garbage from the HTML and takes only text elements
    from the page.

    :param response: HTTP Response.
    :return: String: Text only stripped response.
    """
    soup = BeautifulSoup(response, features="lxml")
    for s in soup(['script', 'style']):
        s.decompose()

    return ' '.join(soup.stripped_strings)


def _make_request_with_ua(url, random_ua=False, random_proxy=False, timeout=10):
    """ Makes an HTTP request with optional random user-agent and proxy.
    
    :param url: String - URL to request
    :param random_ua: Boolean - Whether to use random user-agent
    :param random_proxy: Boolean - Whether to use random proxy
    :param timeout: Integer - Request timeout in seconds
    :return: bytes - Response content
    """
    # Set up proxy if random proxy is enabled
    if random_proxy:
        proxy = get_random_proxy()
        if proxy:
            setup_proxy_connection(proxy)
    
    # Set up user-agent if random UA is enabled
    if random_ua:
        user_agent = get_random_user_agent()
        if user_agent:
            req = urllib.request.Request(url, headers={'User-Agent': user_agent})
            return urllib.request.urlopen(req, timeout=timeout).read()
    return urllib.request.urlopen(url, timeout=timeout).read()


def check_yara(raw=None, yara=0):
    """ Validates Yara Rule to categorize the site and check for keywords.

    :param raw: HTTP Response body.
    :param yara:  Integer: Keyword search argument.
    :return matches: List of yara rule matches.
    """

    try:
        import yara as _yara
    except OSError:
        print("YARA module error: " + 
              "Try this solution: https://stackoverflow.com/a/51504326")

    try:
        file_path = resources.files("res").joinpath("keywords.yar")
    except (FileNotFoundError, ModuleNotFoundError):
        file_path = os.path.join('res/keywords.yar')

    if raw is not None:
        if yara == 1:
            raw = text(response=raw).lower()

        file = os.path.join(file_path)
        rules = _yara.compile(str(file))
        matches = rules.match(data=raw)
        if len(matches) != 0:
            print("YARA: Found a match!")
        return matches


def input_file_to_folder(input_file, output_path, yara=None, random_ua=False, random_proxy=False):
    """ Ingests the crawled links from the input_file,
    scrapes the contents of the resulting web pages and writes the contents to
    the into out_path/{url_address}.

    :param input_file: String: Filename of the crawled Urls.
    :param output_path: String: Pathname of results.
    :param yara: Integer: Keyword search argument.
    :param random_ua: Boolean: Whether to use random user-agent rotation.
    :param random_proxy: Boolean: Whether to use random proxy rotation.
    :return: None
    """
    i = 0
    file = io.TextIOWrapper
    try:
        file = open(input_file, 'r')
    except IOError as err:
        print(f"Error: {err}\n## Can't open: {input_file}")

    for line in file:

        # Generate the name for every file.
        try:
            page_name = line.rsplit('/', 1)
            cl_page_name = str(page_name[1])
            cl_page_name = cl_page_name[:-1]
            if len(cl_page_name) == 0:
                output_file = "index.htm"
            else:
                output_file = cl_page_name
        except IndexError as error:
            print(f"Error: {error}")
            continue

        # Extract page to file.
        try:
            content = _make_request_with_ua(line, random_ua, random_proxy, timeout=10)

            if yara is not None:
                full_match_keywords = check_yara(content, yara)
                if len(full_match_keywords) == 0:
                    print('No matches found.')
                    continue

            # Add an incremental in case of existing filename (eg. index.htm)
            filename = Path(output_path + "/" + output_file)
            if filename.is_file():
                i += 1
                filename = output_path + "/" + output_file + "(" + str(i) + ")"
            with open(filename, 'wb') as results:
                results.write(content)
            print(f"# File created on: {os.getcwd()}/{filename}")
        except HTTPError as e:
            print(f"Error: {e.code}, cannot access: {e.url}")
            continue
        except InvalidURL:
            print(f"Invalid URL: {line}, \n Skipping...")
            continue
        except IncompleteRead:
            print(f"IncompleteRead on {line}")
            continue
        except IOError as err:
            print(f"Error: {err}\nCan't write on file: {output_file}")
    file.close()


def input_file_to_terminal(input_file, yara, random_ua=False, random_proxy=False):
    """ Input links from file and extract them into terminal.

    :param input_file: String: File name of links file.
    :param yara: Integer: Keyword search argument.
    :param random_ua: Boolean: Whether to use random user-agent rotation.
    :param random_proxy: Boolean: Whether to use random proxy rotation.
    :return: None
    """
    try:
        with open(input_file, 'r') as file:
            for line in file:
                website = url_canon(line, 0)
                try:
                    content = _make_request_with_ua(website, random_ua, random_proxy)
                except (HTTPError, URLError, InvalidURL) as err:
                    print(f"## ERROR: {err}. URL: " + website)
                    continue
                if yara is not None:
                    full_match_keywords = check_yara(raw=content, yara=yara)

                    if len(full_match_keywords) == 0:
                        print(f"No matches in: {line}")
                print(content)
    except IOError as err:
        print(f"ERROR: {err}\n## Not valid file. File tried: " + input_file)


def url_to_folder(website, output_file, output_path, yara, random_ua=False, random_proxy=False):
    """ Scrapes the contents of the provided web address and outputs the
    contents to file.

    :param website: String: Url of web address to scrape.
    :param output_file: String: Filename of the results.
    :param output_path: String: Folder name of the output findings.
    :param yara: Integer: Keyword search argument.
    :param random_ua: Boolean: Whether to use random user-agent rotation.
    :param random_proxy: Boolean: Whether to use random proxy rotation.
    :return: None
    """
    # Extract page to file
    try:
        output_file = output_path + "/" + output_file
        content = _make_request_with_ua(website, random_ua, random_proxy)

        if yara is not None:
            full_match_keywords = check_yara(raw=content, yara=yara)

            if len(full_match_keywords) == 0:
                print(f"No matches in: {website}")

        with open(output_file, 'wb') as file:
            file.write(content)
        print(f"## File created on: {os.getcwd()}/{output_file}")
    except (HTTPError, URLError, InvalidURL) as err:
        print(f"HTTPError: {err}")
    except IOError as err:
        print(f"Error: {err}\n Can't write on file: {output_file}")


def url_to_terminal(website, yara, random_ua=False, random_proxy=False):
    """ Scrapes provided web address and prints the results to the terminal.

    :param website: String: URL of website to scrape.
    :param yara: Integer: Keyword search argument.
    :param random_ua: Boolean: Whether to use random user-agent rotation.
    :param random_proxy: Boolean: Whether to use random proxy rotation.
    :return: None
    """
    try:
        content = _make_request_with_ua(website, random_ua, random_proxy)
        if yara is not None:
            full_match_keywords = check_yara(content, yara)

            if len(full_match_keywords) == 0:
                # No match.
                print(f"No matches in: {website}")
                return

        print(content)
    except (HTTPError, URLError, InvalidURL) as err:
        print(f"Error: ({err}) {website}")
        return


def extractor(website, crawl, output_file, input_file, output_path, selection_yara, random_ua=False, random_proxy=False):
    """ Extractor - scrapes the resulting website or discovered links.

    :param website: String: URL of website to scrape.
    :param crawl: Boolean: input_file_to_folder trigger.
        If used iteratively scrape the urls from input_file.
    :param output_file: String: Filename of resulting output from scrape.
    :param input_file: String: Filename of crawled/discovered URLs
    :param output_path: String: Dir path for output files.
    :param selection_yara: String: Selected option of HTML or Text.
    :param random_ua: Boolean: Whether to use random user-agent rotation.
    :param random_proxy: Boolean: Whether to use random proxy rotation.
    :return: None
    """
    if len(input_file) > 0:
        if crawl:
            input_file_to_folder(input_file, output_path, selection_yara, random_ua, random_proxy)
        # TODO: Extract from list into a folder
        # elif len(output_file) > 0:
        # 	input_list_to_folder(website, input_ile, output_file)
        else:
            input_file_to_terminal(input_file, selection_yara, random_ua, random_proxy)
    else:
        if len(output_file) > 0:
            url_to_folder(website, output_file, output_path, selection_yara, random_ua, random_proxy)
        else:
            url_to_terminal(website, selection_yara, random_ua, random_proxy)
