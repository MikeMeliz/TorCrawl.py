#!/usr/bin/python
import http.client
import os
import re
import sys
import datetime
import time
import urllib.request
from urllib.parse import urlparse, urljoin
from collections import defaultdict
from urllib.error import HTTPError, URLError

from bs4 import BeautifulSoup
from modules.checker import get_random_user_agent
from modules.checker import get_random_proxy
from modules.checker import setup_proxy_connection

DEFAULT_URL_REGEX = r'(?:(?:https?|ftp|file):\/\/|www\.)[^\s"\'<>]+'
DEFAULT_REGEX_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, 'res', 'regex_patterns.txt')
)
IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp')


class Crawler:
    def __init__(self, website, c_depth, c_pause, out_path, logs, verbose,
                 random_ua=False, random_proxy=False):
        self.website = website
        self.c_depth = c_depth
        self.c_pause = c_pause
        self.out_path = out_path
        self.logs = logs
        self.verbose = verbose
        self.random_ua = random_ua
        self.random_proxy = random_proxy
        self.regex_patterns = self._load_regex_patterns()
        self.timestamp = datetime.datetime.now().strftime("%y%m%d")
        parsed = urlparse(self.website)
        netloc = parsed.netloc.lower()
        self.base_domain = netloc[4:] if netloc.startswith("www.") else netloc
        self.findings = {
            "links": set(),
            "external_links": set(),
            "images": set(),
            "scripts": set(),
            "telephones": set(),
            "emails": set(),
            "files": set(),
        }
        self.normalized_links = set()
        self.logged = {
            "external_links": set(),
            "images": set(),
            "scripts": set(),
            "telephones": set(),
            "emails": set(),
            "files": set(),
        }
        self.resources = {
            "external_links": defaultdict(set),
            "images": defaultdict(set),
            "scripts": defaultdict(set),
            "telephones": defaultdict(set),
            "emails": defaultdict(set),
            "files": defaultdict(set),
        }
        self.edges = set()
        self.titles = {}

    def _load_regex_patterns(self):
        """Load regex patterns from res/regex_patterns.txt plus default URL pattern."""
        patterns = [DEFAULT_URL_REGEX]

        # Only read patterns from the dedicated file.
        try:
            if os.path.exists(DEFAULT_REGEX_FILE):
                with open(DEFAULT_REGEX_FILE, 'r', encoding='UTF-8') as pattern_file:
                    for line in pattern_file:
                        stripped = line.strip()
                        if stripped and not stripped.startswith('#'):
                            patterns.append(stripped)
        except OSError as err:
            print(f"## Unable to read regex pattern file {DEFAULT_REGEX_FILE}: {err}")
            self.write_log(f"[INFO] WARN: Unable to read regex pattern file {DEFAULT_REGEX_FILE}: {err}\n")

        compiled_patterns = []
        for pattern in patterns:
            try:
                compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error as err:
                print(f"## Skipping invalid regex pattern '{pattern}': {err}")
                self.write_log(f"[INFO] WARN: Skipping invalid regex pattern '{pattern}': {err}\n")

        return compiled_patterns

    def excludes(self, link, source_url=None):
        """ Excludes links that are not required.

        :param link: String
        :return: Boolean
        """
        now = self.timestamp
        source = source_url or self.website

        # Normalize domain comparison for absolute links to treat same-domain (with/without www)
        same_domain = False
        if isinstance(link, str) and link.startswith(('http://', 'https://')):
            try:
                parsed = urlparse(link)
                netloc = parsed.netloc.lower()
                candidate_domain = netloc[4:] if netloc.startswith("www.") else netloc
                same_domain = candidate_domain == self.base_domain
            except ValueError:
                # Malformed URL; let the regular exclusion rules handle (or skip)
                return True

        # BeautifulSoup returns tags without href; skip missing targets early
        if link is None:
            return True
        # Links
        elif '#' in link:
            return True
        # Image links (log separately only)
        elif self._is_image_link(link):
            img_path = self.out_path + '/' + now + '_images.txt'
            self._log_once("images", link, img_path)
            self.findings["images"].add(str(link))
            self.resources["images"][source].add(str(link))
            return True
        # Script links (log separately only)
        elif re.search('^.*\\.(js|mjs|ts|jsx|tsx)$', link, re.IGNORECASE):
            script_path = self.out_path + '/' + now + '_scripts.txt'
            self._log_once("scripts", link, script_path)
            self.findings["scripts"].add(str(link))
            self.resources["scripts"][source].add(str(link))
            return True
        # External links
        elif link.startswith('http') and not same_domain:
            file_path = self.out_path + '/' + now + '_ext-links.txt'
            self._log_once("external_links", link, file_path)
            self.findings["external_links"].add(str(link))
            self.resources["external_links"][source].add(str(link))
            return True
        # Telephone Number
        elif link.startswith('tel:'):
            link = link.replace('tel:', '', 1)
            file_path = self.out_path + '/' + now + '_telephones.txt'
            self._log_once("telephones", link, file_path)
            self.findings["telephones"].add(str(link))
            self.resources["telephones"][source].add(str(link))
            return True
        # Mails
        elif link.startswith('mailto:'):
            link = link.replace('mailto:', '', 1)
            file_path = self.out_path + '/' + now + '_mails.txt'
            self._log_once("emails", link, file_path)
            self.findings["emails"].add(str(link))
            self.resources["emails"][source].add(str(link))
            return True
        # Other files
        elif re.search('^.*\\.(pdf|doc)$', link, re.IGNORECASE):
            file_path = self.out_path + '/' + now + '_files.txt'
            self._log_once("files", link, file_path)
            self.findings["files"].add(str(link))
            return True

    def canonical(self, link):
        """ Canonicalization of the link.

        :param link: String: URL(s)
        :return: String 'final_link': parsed canonical url.
        """
        # Already formatted
        if link.startswith(self.website):
            return link
        # Absolute URL with same base domain but different subdomain (e.g., missing www)
        if link.startswith(('http://', 'https://')):
            try:
                parsed = urlparse(link)
                netloc = parsed.netloc.lower()
                candidate_domain = netloc[4:] if netloc.startswith("www.") else netloc
                if candidate_domain == self.base_domain:
                    return link
            except ValueError:
                return None
        # For relative paths with / in front
        elif link.startswith('/'):
            if self.website[-1] == '/':
                final_link = self.website[:-1] + link
            else:
                final_link = self.website + link
            return final_link
        # For relative paths without leading slash (e.g., "about", "services/", "?q=1")
        elif not link.startswith('http') and not link.startswith('//'):
            return urljoin(self.website if self.website.endswith('/') else self.website + '/', link)
        # Protocol-relative URLs
        elif link.startswith('//'):
            parsed_base = urlparse(self.website)
            return f"{parsed_base.scheme}:{link}"

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
        self.findings["links"].add(self.website)
        self.normalized_links.add(self._normalize_for_dedupe(self.website))
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
                    raw_content = html_page.read()
                    if isinstance(raw_content, (bytes, bytearray)):
                        html_content = raw_content.decode('utf-8', errors='ignore')
                    else:
                        html_content = str(raw_content)
                except Exception:
                    self.write_log(f"[INFO] ERROR: Unable to read content from: {str(item)}\n")
                    continue

                try:
                    soup = BeautifulSoup(html_content, features="html.parser")
                except TypeError:
                    print(f"## Soup Error Encountered:: couldn't parse "
                          f"ord_list # {ord_lst_ind}::{ord_lst[ord_lst_ind]}")
                    continue

                source_url = item if item else self.website
                page_title = None
                if soup.title and soup.title.string:
                    page_title = soup.title.string.strip()
                self.titles[source_url] = page_title

                # For each <a href=""> tag.
                for link in soup.find_all('a'):
                    link = link.get('href')

                    if self.excludes(link, source_url):
                        continue

                    ver_link = self.canonical(link)
                    if ver_link is not None:
                        self._add_link(ver_link, source_url, lst)
                        self.edges.add((source_url, ver_link))

                # For each <area> tag.
                for link in soup.find_all('area'):
                    link = link.get('href')

                    if self.excludes(link, source_url):
                        continue

                    ver_link = self.canonical(link)
                    if ver_link is not None:
                        self._add_link(ver_link, source_url, lst)
                        self.edges.add((source_url, ver_link))

                # Additional regex sweep for links not inside <a> or <area> tags.
                if self.verbose:
                    # print("## Starting RegEx parsing of the page")
                    pass
                for pattern in self.regex_patterns:
                    if self.verbose:
                        # print(f"## Parsing with regex: {pattern.pattern}")
                        pass
                    for match in pattern.finditer(html_content):
                        link = match.group(0).rstrip('),.;\'"')
                        if link.startswith('www.'):
                            link = f"https://{link}"
                        if self.excludes(link, source_url):
                            continue
                        ver_link = self.canonical(link)
                        if ver_link is not None:
                            self._add_link(ver_link, source_url, lst)
                            self.edges.add((source_url, ver_link))

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

    def _serialized_findings(self):
        """Return findings as JSON-serializable dict."""
        return {
            "start_url": self.website,
            "links": sorted(self.findings["links"]),
            "external_links": sorted(self.findings["external_links"]),
            "images": sorted(self.findings["images"]),
            "scripts": sorted(self.findings["scripts"]),
            "telephones": sorted(self.findings["telephones"]),
            "emails": sorted(self.findings["emails"]),
            "files": sorted(self.findings["files"]),
        }

    def _normalize_for_dedupe(self, url):
        """Normalize URL for deduplication: lower-case host, strip leading www."""
        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            netloc = netloc[4:] if netloc.startswith("www.") else netloc
            normalized = parsed._replace(netloc=netloc).geturl()
            return normalized
        except ValueError:
            return url.strip().lower()

    def _add_link(self, ver_link, source_url, lst):
        """Add link to collections with deduplication by normalized host."""
        norm = self._normalize_for_dedupe(ver_link)
        if norm not in self.normalized_links:
            self.normalized_links.add(norm)
            lst.add(ver_link)
            self.findings["links"].add(ver_link)
        # Always record edge relationships, even if link already known
        if source_url and ver_link:
            self.edges.add((source_url, ver_link))

    def _log_once(self, category, link, filepath):
        """Log to file only if normalized link not already written."""
        norm = self._normalize_for_dedupe(link)
        if norm in self.logged.get(category, set()):
            return
        self.logged.setdefault(category, set()).add(norm)
        with open(filepath, 'a+', encoding='UTF-8') as lst_file:
            lst_file.write(str(link) + '\n')

    def _is_image_link(self, link):
        """Best-effort image detection using URL path extension (ignoring query/fragment)."""
        try:
            parsed = urlparse(link)
            path = parsed.path.lower()
        except Exception:
            path = str(link).lower()
        base = path.split('?', 1)[0].split('#', 1)[0]
        return any(base.endswith(ext) for ext in IMAGE_EXTS)

    def export_payload(self):
        """Return data needed for downstream exporters/visualization."""
        return {
            "start_url": self.website,
            "data": self._serialized_findings(),
            "edges": set(self.edges),
            "titles": dict(self.titles),
            "resources": {cat: {src: sorted(vals) for src, vals in sources.items()}
                          for cat, sources in self.resources.items()},
        }
