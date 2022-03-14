#!/usr/bin/python

import re
import sys
import time
import urllib.request
from urllib.error import HTTPError

from bs4 import BeautifulSoup


def excludes(link, website, out_path):
    """ Excludes links that are not required.

    :param link:
    :param website:
    :param out_path:
    :return:
    """
    # BUG: For NoneType Exceptions, got to find a solution here
    if link is None:
        return True
    # Links
    elif '#' in link:
        return True
    # External links
    elif link.startswith('http') and not link.startswith(website):
        with open(out_path + '/extlinks.txt', 'w+') as lst_file:
            lst_file.write(str(link) + '\n')
        return True
    # Telephone Number
    elif link.startswith('tel:'):
        with open(out_path + '/telephones.txt', 'w+') as lst_file:
            lst_file.write(str(link) + '\n')
        return True
    # Mails
    elif link.startswith('mailto:'):
        with open(out_path + '/mails.txt', 'w+') as lst_file:
            lst_file.write(str(link) + '\n')
        return True
    # Type of files
    elif re.search('^.*\.(pdf|jpg|jpeg|png|gif|doc)$', link, re.IGNORECASE):
        return True


def canonical(link, website):
    """ Canonization of the link.

    :param link:
    :param website:
    :return:
    """
    # Already formatted
    if link.startswith(website):
        return link
    # For relative paths with / in front
    elif link.startswith('/'):
        if website[-1] == '/':
            final_link = website[:-1] + link
        else:
            final_link = website + link
        return final_link
    # For relative paths without /
    elif re.search('^.*\.(html|htm|aspx|php|doc|css|js|less)$', link,
                   re.IGNORECASE):
        # Pass to
        if website[-1] == '/':
            final_link = website + link
        else:
            final_link = website + "/" + link
        return final_link


# Clean links from '?page=' arguments


def crawler(website, c_depth, c_pause, out_path, logs, verbose):
    """ Core of the crawler.

    :param website:
    :param c_depth:
    :param c_pause:
    :param out_path:
    :param logs:
    :param verbose:
    :return:
    """
    lst = set()
    ord_lst = []
    ord_lst.insert(0, website)
    ord_lstind = 0

    if logs:
        global log_file
        log_file = open(out_path + '/log.txt', 'w+')

    print(f"## Crawler started from {website} with {str(c_depth)} depth "
          f"crawl, and {str(c_pause)} second(s) delay.")

    # Depth
    for x in range(0, int(c_depth)):

        # For every element of list
        for item in ord_lst:

            # Check if is the first element
            if ord_lstind > 0:
                try:
                    if item is not None:
                        global html_page
                        html_page = urllib.request.urlopen(item)
                except HTTPError as error:
                    print(error)
            else:
                html_page = urllib.request.urlopen(website)
                ord_lstind += 1

            soup = BeautifulSoup(html_page, features="html.parser")

            # For each <a href=""> tag
            for link in soup.findAll('a'):
                link = link.get('href')

                if excludes(link, website, out_path):
                    continue

                ver_link = canonical(link, website)
                lst.add(ver_link)

            # For each <area> tag
            for link in soup.findAll('area'):
                link = link.get('href')

                if excludes(link, website, out_path):
                    continue

                ver_link = canonical(link, website)
                lst.add(ver_link)

            # TODO: For images
            # TODO: For scripts

            # Pass new on list and re-set it to delete duplicates
            ord_lst = ord_lst + list(set(lst))
            ord_lst = list(set(ord_lst))

            if verbose:
                sys.stdout.write("-- Results: " + str(len(ord_lst)) + "\r")
                sys.stdout.flush()

            # Pause time
            if (ord_lst.index(item) != len(ord_lst) - 1) and \
                    float(c_pause) > 0:
                time.sleep(float(c_pause))

            # Keeps logs for every webpage visited
            if logs:
                it_code = html_page.getcode()
                log_file.write("[" + str(it_code) + "] " + str(item) + "\n")

        print(("## Step " + str(x + 1) + " completed with: " + str(
            len(ord_lst)) + " result(s)"))

    if logs:
        log_file.close()

    return ord_lst
