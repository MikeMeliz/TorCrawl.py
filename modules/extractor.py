#!/usr/bin/python
import io
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError


def cinex(input_file, out_path):
    """ Ingests the crawled links from the input_file,
    scrapes the contents of the resulting web pages and writes the contents to
    the into out_path/{url_address}.

    :param input_file: String: Filename of the crawled Urls.
    :param out_path: String: Pathname of results.
    :return: None
    """
    file = io.TextIOWrapper
    try:
        file = open(input_file, 'r')
    except IOError as err:
        # error = sys.exc_info()[0]
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

        # Extract page to file
        try:
            with open(out_path + "/" + output_file, 'wb') as results:
                results.write(urllib.request.urlopen(line).read())
            print(f"# File created on: {os.getcwd()}/{out_path}/{output_file}")
        except IOError as err:
            error = sys.exc_info()[0]
            print(f"Error: {error}\nCan't write on file: {output_file}")
    file.close()


def intermex(input_file):
    """ Input links from file and extract them into terminal.

    :param input_file: String: File name of links file.
    :return: None
    """
    try:
        with open(input_file, 'r') as file:
            for line in file:
                print((urllib.request.urlopen(line).read()))
    except (HTTPError, URLError) as err:
        print(f"HTTPError: {err}")
    except IOError as err:
        # error = sys.exc_info()[0]
        print(f"Error: {err}\n## Not valid file")


def outex(website, output_file, out_path):
    """ Scrapes the contents of the provided web address and outputs the
    contents to file.

    :param website: String: Url of web address to scrape.
    :param output_file: String: Filename of the results.
    :param out_path: String: Folder name of the output findings.
    :return: None
    """
    # Extract page to file
    try:
        output_file = out_path + "/" + output_file
        with open(output_file, 'wb') as file:
            file.write(urllib.request.urlopen(website).read())
        print(f"## File created on: {os.getcwd()}/{output_file}")
    except (HTTPError, URLError) as err:
        print(f"HTTPError: {err}")
    except IOError as err:
        # error = sys.exc_info()[0]
        print(f"Error: {err}\n Can't write on file: {output_file}")


def termex(website):
    """ Scrapes provided web address and prints the results to the terminal.

    :param website: String: URL of website to scrape.
    :return: None
    """
    try:
        print((urllib.request.urlopen(website).read()))
    except (urllib.error.HTTPError, urllib.error.URLError) as err:
        print(f"Error: ({err}) {website}")
        return


def extractor(website, crawl, output_file, input_file, out_path):
    """ Extractor - scrapes the resulting website or discovered links.

    :param website: String: URL of website to scrape.
    :param crawl: Boolean: Cinex trigger.
        If used iteratively scrape the urls from input_file.
    :param output_file: String: Filename of resulting output from scrape.
    :param input_file: String: Filename of crawled/discovered URLs
    :param out_path: String: Dir path for output files.
    :return: None
    """
    # TODO: Return output to torcrawl.py
    if len(input_file) > 0:
        if crawl:
            cinex(input_file, out_path)
        # TODO: Extract from list into a folder
        # elif len(output_file) > 0:
        # 	inoutex(website, input_ile, output_file)
        else:
            intermex(input_file)
    else:
        if len(output_file) > 0:
            outex(website, output_file, out_path)
        else:
            termex(website)
