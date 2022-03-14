#!/usr/bin/python

import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def cinex(input_file, out_path):
    """ Ingests the input links from file and extract them into path/files.

    :param input_file:
    :param out_path:
    :return:
    """
    try:
        global f
        f = open(input_file, 'r')
    except IOError as err:
        error = sys.exc_info()[0]
        print(f"Error: {error}\n## Can't open: {input_file}")

    for line in f:

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
            with open(out_path + "/" + output_file, 'wb') as f:
                f.write(urllib.request.urlopen(line).read())
            print(f"# File created on: {os.getcwd()}/{out_path}/{output_file}")
        except IOError as err:
            error = sys.exc_info()[0]
            print(f"Error: {error}\n Can't write on file: {output_file}")


def intermex(input_file):
    """ Input links from file and extract them into terminal.

    :param input_file:
    :return:
    """
    try:
        with open(input_file, 'r') as f:
            for line in f:
                print((urllib.request.urlopen(line).read()))
    except IOError as err:
        error = sys.exc_info()[0]
        print(f"Error: {error}\n## Not valid file")


def outex(website, output_file, out_path):
    """ Output the contents of the webpage into a file.

    :param website:
    :param output_file:
    :param out_path:
    :return:
    """
    # Extract page to file
    try:
        output_file = out_path + "/" + output_file
        with open(output_file, 'wb') as f:
            f.write(urllib.request.urlopen(website).read())
        print(f"## File created on: {os.getcwd()}/{output_file}")
    except IOError as err:
        error = sys.exc_info()[0]
        print(f"Error: {error}\n Can't write on file: {output_file}")


def termex(website):
    """ Output findings to the terminal.

    :param website:
    :return:
    """
    try:
        print((urllib.request.urlopen(website).read()))
    except (urllib.error.HTTPError, urllib.error.URLError) as err:
        print(f"Error: ({err}) {website}")
        return None


def extractor(website, crawl, output_file, input_ile, out_path):
    """

    :param website:
    :param crawl:
    :param output_file:
    :param input_ile:
    :param out_path:
    :return:
    """
    # TODO: Return output to torcrawl.py
    if len(input_ile) > 0:
        if crawl:
            cinex(input_ile, out_path)
        # TODO: Extract from list into a folder
        # elif len(output_file) > 0:
        # 	inoutex(website, input_ile, output_file)
        else:
            intermex(input_ile)
    else:
        if len(output_file) > 0:
            outex(website, output_file, out_path)
        else:
            termex(website)
