#!/usr/bin/python
import http.client
import os
import re
import sys
import time
import urllib.request
from urllib.error import HTTPError

from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, website, c_depth, c_pause, out_path, logs, verbose):
        self.website = website
        self.c_depth = c_depth
        self.c_pause = c_pause
        self.out_path = out_path
        self.logs = logs
        self.verbose = verbose

    def excludes(self, link):
        """ Excludes links that are not required.

        :param link:
        :return: Boolean
        """
        # BUG: For NoneType Exceptions, got to find a solution here
        if link is None:
            return True
        # Links
        elif '#' in link:
            return True
        # External links
        elif link.startswith('http') and not link.startswith(self.website):
            file_path = self.out_path + '/extlinks.txt'
            with open(file_path, 'w+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            return True
        # Telephone Number
        elif link.startswith('tel:'):
            file_path = self.out_path + '/telephones.txt'
            with open(file_path, 'w+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            return True
        # Mails
        elif link.startswith('mailto:'):
            file_path = self.out_path + '/mails.txt'
            with open(file_path, 'w+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            return True
        # Type of files
        elif re.search('^.*\\.(pdf|jpg|jpeg|png|gif|doc)$', link,
                       re.IGNORECASE):
            return True

    def canonical(self, link):
        """ Canonization of the link.

        :param link:
        :return:
        """
        # Already formatted
        if link.startswith(self.website):
            return link
        # For relative paths with / in front
        elif link.startswith('/'):
            if self.website[-1] == '/':
                final_link = self.website[:-1] + link
            else:
                final_link = self.website + link
            return final_link
        # For relative paths without /
        elif re.search('^.*\\.(html|htm|aspx|php|doc|css|js|less)$', link,
                       re.IGNORECASE):
            # Pass to
            if self.website[-1] == '/':
                final_link = self.website + link
            else:
                final_link = self.website + "/" + link
            return final_link

    def crawl(self):
        """ Core of the crawler.
        :return: List (ord_lst) - List of crawled links.
        """
        lst = set()
        ord_lst = []
        ord_lst.insert(0, self.website)
        ord_lst_ind = 0
        log_path = self.out_path + '/log.txt'

        if self.logs is True and os.access(log_path, os.W_OK) is False:
            print(f"## Unable to write to {self.out_path}/log.txt - Exiting")
            sys.exit(2)

        print(f"## Crawler started from {self.website} with "
              f"{str(self.c_depth)} depth crawl, and {str(self.c_pause)} "
              f"second(s) delay.")

        # Depth
        for index in range(0, int(self.c_depth)):

            # For every element of list.
            for item in ord_lst:
                html_page = http.client.HTTPResponse
                # Check if is the first element
                if ord_lst_ind > 0:
                    try:
                        if item is not None:
                            html_page = urllib.request.urlopen(item)
                    except HTTPError as error:
                        print(error)
                        continue
                else:
                    try:
                        html_page = urllib.request.urlopen(self.website)
                        ord_lst_ind += 1
                    except HTTPError as error:
                        print(error)
                        ord_lst_ind += 1
                        continue

                try:
                    soup = BeautifulSoup(html_page, features="html.parser")
                except TypeError as err:
                    print(f"## Soup Error Encountered:: could to parse "
                          f"ord_list # {ord_lst_ind}::{ord_lst[ord_lst_ind]}")
                    continue

                # For each <a href=""> tag.
                for link in soup.findAll('a'):
                    link = link.get('href')

                    if self.excludes(link):
                        continue

                    ver_link = self.canonical(link)
                    if ver_link is not None:
                        lst.add(ver_link)

                # For each <area> tag.
                for link in soup.findAll('area'):
                    link = link.get('href')

                    if self.excludes(link):
                        continue

                    ver_link = self.canonical(link)
                    if ver_link is not None:
                        lst.add(ver_link)

                # TODO: For images
                # TODO: For scripts

                # Pass new on list and re-set it to delete duplicates.
                ord_lst = ord_lst + list(set(lst))
                ord_lst = list(set(ord_lst))

                if self.verbose:
                    sys.stdout.write("-- Results: " + str(len(ord_lst)) + "\r")
                    sys.stdout.flush()

                # Pause time.
                if (ord_lst.index(item) != len(ord_lst) - 1) and \
                        float(self.c_pause) > 0:
                    time.sleep(float(self.c_pause))

                # Keeps logs for every webpage visited.
                if self.logs:
                    it_code = html_page.getcode()
                    with open(log_path, 'w+', encoding='UTF-8') as log_file:
                        log_file.write(f"[{str(it_code)}] {str(item)} \n")

            print(f"## Step {str(index + 1)} completed \n\t "
                  f"with: {str(len(ord_lst))} result(s)")

        return ord_lst
