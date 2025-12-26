#!/usr/bin/python
import http.client
import os
import re
import sys
import datetime
import time
import urllib.request
from urllib.error import HTTPError, URLError

from bs4 import BeautifulSoup
from modules.checker import get_random_user_agent
from modules.checker import get_random_proxy
from modules.checker import setup_proxy_connection


class Crawler:
    def __init__(self, website, c_depth, c_pause, out_path, logs, verbose, random_ua=False, random_proxy=False):
        self.website = website
        self.c_depth = c_depth
        self.c_pause = c_pause
        self.out_path = out_path
        self.logs = logs
        self.verbose = verbose
        self.random_ua = random_ua
        self.random_proxy = random_proxy

    def excludes(self, link):
        """ Excludes links that are not required.

        :param link: String
        :return: Boolean
        """
        now = datetime.datetime.now().strftime("%y%m%d")

        # BUG: For NoneType Exceptions, got to find a solution here
        if link is None:
            return True
        # Links
        elif '#' in link:
            return True
        # External links
        elif link.startswith('http') and not link.startswith(self.website):
            file_path = self.out_path + '/' + now + '_ext-links.txt'
            with open(file_path, 'a+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            return True
        # Telephone Number
        elif link.startswith('tel:'):
            file_path = self.out_path + '/' + now + '_telephones.txt'
            with open(file_path, 'a+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            return True
        # Mails
        elif link.startswith('mailto:'):
            file_path = self.out_path + '/' + now + '_mails.txt'
            with open(file_path, 'a+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            return True
        # Type of files
        elif re.search('^.*\\.(pdf|jpg|jpeg|png|gif|doc)$', link, re.IGNORECASE):
            file_path = self.out_path + '/' + now + '_files.txt'
            with open(file_path, 'a+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            return True

    def canonical(self, link):
        """ Canonicalization of the link.

        :param link: String: URL(s)
        :return: String 'final_link': parsed canonical url.
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

    def write_log(self, log):
        log_path = self.out_path + '/crawler.log'
        now = datetime.datetime.now()

        if self.logs is True:
            open(log_path, 'a+')
            if self.logs is True and os.access(log_path, os.W_OK) is False:
                print(f"## Unable to write to {self.out_path}/log.txt - Exiting")
                sys.exit(2)
            with open(log_path, 'a+', encoding='UTF-8') as log_file:
                log_file.write(str(now) + " [crawler.py] " + log)
                log_file.close()

    def _make_request(self, url):
        """ Makes an HTTP request with optional random user-agent and proxy.
        
        :param url: String - URL to request
        :return: HTTPResponse object
        """
        # Set up proxy if random proxy is enabled
        if self.random_proxy:
            proxy = get_random_proxy()
            if proxy:
                setup_proxy_connection(proxy)
        
        # Set up user-agent if random UA is enabled
        if self.random_ua:
            user_agent = get_random_user_agent()
            if user_agent:
                req = urllib.request.Request(url, headers={'User-Agent': user_agent})
                return urllib.request.urlopen(req)
        return urllib.request.urlopen(url)


    def crawl(self):
        """ Core of the crawler.
        :return: List (ord_lst) - List of crawled links.
        """
        lst = set()
        ord_lst = []
        ord_lst.insert(0, self.website)
        ord_lst_ind = 0

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
                            html_page = self._make_request(item)
                    except (HTTPError, URLError) as error:
                        self.write_log(f"[INFO] ERROR: Domain or link seems to be unreachable: {str(item)} | "
                                       f"Message: {error}\n")
                        continue
                else:
                    try:
                        html_page = self._make_request(self.website)
                        ord_lst_ind += 1
                    except (HTTPError, URLError) as error:
                        self.write_log(f"[INFO] ERROR: Domain or link seems to be unreachable: {str(item)} | "
                                       f"Message: {error}\n")
                        ord_lst_ind += 1
                        continue

                try:
                    soup = BeautifulSoup(html_page, features="html.parser")
                except TypeError:
                    print(f"## Soup Error Encountered:: couldn't parse "
                          f"ord_list # {ord_lst_ind}::{ord_lst[ord_lst_ind]}")
                    continue

                # For each <a href=""> tag.
                for link in soup.find_all('a'):
                    link = link.get('href')

                    if self.excludes(link):
                        continue

                    ver_link = self.canonical(link)
                    if ver_link is not None:
                        lst.add(ver_link)

                # For each <area> tag.
                for link in soup.find_all('area'):
                    link = link.get('href')

                    if self.excludes(link):
                        continue

                    ver_link = self.canonical(link)
                    if ver_link is not None:
                        lst.add(ver_link)

                # TODO: For non-formal links, using RegEx, should be an additional parameter, and all patterns to be stored in a file
                # url_pattern = r'/(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])/igm'
                # html_content = urllib.request.urlopen(self.website).read().decode('utf-8')
                
                # if self.verbose:
                #     print("## Starting RegEx parsing of the page")
                # found_regex = re.findall(url_pattern, html_content)
                # for link in found_regex:
                #     if self.excludes(link):
                #         continue
                #     ver_link = self.canonical(link)
                #     if ver_link is not None:
                #         lst.add(ver_link)

                # TODO: For images
                # TODO: For scripts

                # Pass new on list and re-set it to delete duplicates.
                ord_lst = ord_lst + list(set(lst))
                ord_lst = list(set(ord_lst))

                # Keeps logs for every webpage visited.
                page_code = html_page.status
                url_visited = f"[{str(page_code)}] {str(item)} \n"
                self.write_log("[INFO] Parsed: " + url_visited)

                if self.verbose:
                    sys.stdout.write(" -- Results: " + str(len(ord_lst)) + "\r")
                    sys.stdout.flush()

                # Add Pause time between each iteration
                if (ord_lst.index(item) != len(ord_lst) - 1) and float(self.c_pause) > 0:
                    time.sleep(float(self.c_pause))

            print(f"## Step {str(index + 1)} completed "
                  f"with: {str(len(ord_lst))} result(s)")

        return ord_lst
