#!/usr/bin/python
import http.client
import os
import re
import sys
import datetime
import time
import urllib.request
from urllib.error import HTTPError, URLError
import json
import xml.etree.ElementTree as ET
import sqlite3

from bs4 import BeautifulSoup
from modules.checker import get_random_user_agent
from modules.checker import get_random_proxy
from modules.checker import setup_proxy_connection

DEFAULT_URL_REGEX = r'(?:(?:https?|ftp|file):\/\/|www\.)[^\s"\'<>]+'
DEFAULT_REGEX_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, 'res', 'regex_patterns.txt')
)


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
        self.findings = {
            "links": set(),
            "external_links": set(),
            "images": set(),
            "scripts": set(),
            "telephones": set(),
            "emails": set(),
            "files": set(),
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

    def excludes(self, link):
        """ Excludes links that are not required.

        :param link: String
        :return: Boolean
        """
        now = self.timestamp

        # BeautifulSoup returns tags without href; skip missing targets early
        if link is None:
            return True
        # Links
        elif '#' in link:
            return True
        # Image links (log separately; also record as external when out of scope)
        elif re.search('^.*\\.(jpg|jpeg|png|gif|webp|svg|bmp)$', link, re.IGNORECASE):
            img_path = self.out_path + '/' + now + '_images.txt'
            with open(img_path, 'a+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            self.findings["images"].add(str(link))
            if link.startswith('http') and not link.startswith(self.website):
                file_path = self.out_path + '/' + now + '_ext-links.txt'
                with open(file_path, 'a+', encoding='UTF-8') as lst_file:
                    lst_file.write(str(link) + '\n')
                self.findings["external_links"].add(str(link))
            return True
        # Script links (log separately; also record as external when out of scope)
        elif re.search('^.*\\.(js|mjs|ts|jsx|tsx)$', link, re.IGNORECASE):
            script_path = self.out_path + '/' + now + '_scripts.txt'
            with open(script_path, 'a+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            self.findings["scripts"].add(str(link))
            if link.startswith('http') and not link.startswith(self.website):
                file_path = self.out_path + '/' + now + '_ext-links.txt'
                with open(file_path, 'a+', encoding='UTF-8') as lst_file:
                    lst_file.write(str(link) + '\n')
                self.findings["external_links"].add(str(link))
            return True
        # External links
        elif link.startswith('http') and not link.startswith(self.website):
            file_path = self.out_path + '/' + now + '_ext-links.txt'
            with open(file_path, 'a+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            self.findings["external_links"].add(str(link))
            return True
        # Telephone Number
        elif link.startswith('tel:'):
            file_path = self.out_path + '/' + now + '_telephones.txt'
            with open(file_path, 'a+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            self.findings["telephones"].add(str(link))
            return True
        # Mails
        elif link.startswith('mailto:'):
            file_path = self.out_path + '/' + now + '_mails.txt'
            with open(file_path, 'a+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
            self.findings["emails"].add(str(link))
            return True
        # Other files
        elif re.search('^.*\\.(pdf|doc)$', link, re.IGNORECASE):
            file_path = self.out_path + '/' + now + '_files.txt'
            with open(file_path, 'a+', encoding='UTF-8') as lst_file:
                lst_file.write(str(link) + '\n')
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
        self.findings["links"].add(self.website)
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

                    if self.excludes(link):
                        continue

                    ver_link = self.canonical(link)
                    if ver_link is not None:
                        lst.add(ver_link)
                        self.findings["links"].add(ver_link)
                        self.edges.add((source_url, ver_link))

                # For each <area> tag.
                for link in soup.find_all('area'):
                    link = link.get('href')

                    if self.excludes(link):
                        continue

                    ver_link = self.canonical(link)
                    if ver_link is not None:
                        lst.add(ver_link)
                        self.findings["links"].add(ver_link)
                        self.edges.add((source_url, ver_link))

                # Additional regex sweep for links not inside <a> or <area> tags.
                if self.verbose:
                    print("## Starting RegEx parsing of the page")
                for pattern in self.regex_patterns:
                    if self.verbose:
                        print(f"## Parsing with regex: {pattern.pattern}")
                    for match in pattern.finditer(html_content):
                        link = match.group(0).rstrip('),.;\'"')
                        if link.startswith('www.'):
                            link = f"https://{link}"
                        if self.excludes(link):
                            continue
                        ver_link = self.canonical(link)
                        if ver_link is not None:
                            lst.add(ver_link)
                            self.findings["links"].add(ver_link)
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

    def _build_xml_tree(self, data):
        """Build XML tree from findings data."""
        root = ET.Element("crawl", start_url=data.get("start_url", ""))
        tag_map = {
            "links": "link",
            "external_links": "external_link",
            "images": "image",
            "scripts": "script",
            "telephones": "telephone",
            "emails": "email",
            "files": "file",
        }

        for section, child_tag in tag_map.items():
            section_el = ET.SubElement(root, section)
            for item in data.get(section, []):
                child = ET.SubElement(section_el, child_tag)
                child.text = item
        return root

    def export_findings(self, export_path, prefix, export_json=False, export_xml=False):
        """Export findings to JSON and/or XML while keeping txt outputs intact."""
        data = self._serialized_findings()

        if export_json:
            json_path = os.path.join(export_path, f"{prefix}.json")
            with open(json_path, "w", encoding="UTF-8") as json_file:
                json.dump(data, json_file, indent=2, ensure_ascii=False)
            if self.verbose:
                print(f"## JSON results created at: {json_path}")

        if export_xml:
            xml_path = os.path.join(export_path, f"{prefix}.xml")
            root = self._build_xml_tree(data)
            tree = ET.ElementTree(root)
            tree.write(xml_path, encoding="UTF-8", xml_declaration=True)
            if self.verbose:
                print(f"## XML results created at: {xml_path}")

    def export_database(self, export_path, prefix):
        """Export findings and link relationships to SQLite database."""
        db_path = os.path.join(export_path, f"{prefix}.db")
        data = self._serialized_findings()

        nodes = set(data["links"])
        nodes.update([edge[0] for edge in self.edges])
        nodes.update([edge[1] for edge in self.edges])

        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    url TEXT PRIMARY KEY,
                    title TEXT
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_url TEXT,
                    to_url TEXT
                );
            """)

            cur.executemany(
                "INSERT OR REPLACE INTO nodes(url, title) VALUES(?, ?);",
                [(url, self.titles.get(url)) for url in nodes]
            )

            cur.executemany(
                "INSERT OR IGNORE INTO edges(from_url, to_url) VALUES(?, ?);",
                list(self.edges)
            )
            conn.commit()
            if self.verbose:
                print(f"## SQLite results created at: {db_path}")
        finally:
            conn.close()

    def export_visualization(self, export_path, prefix):
        """Generate an HTML visualization from the SQLite database using NetworkX and PyVis."""
        db_path = os.path.join(export_path, f"{prefix}.db")
        if not os.path.exists(db_path):
            print("## Visualization skipped: database not found. Use --database (-DB).")
            return

        # Load nodes and edges from database
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT url, title FROM nodes;")
            nodes = cur.fetchall()
            cur.execute("SELECT from_url, to_url FROM edges;")
            edges = cur.fetchall()
        finally:
            conn.close()

        import networkx as nx  # type: ignore
        from pyvis.network import Network  # type: ignore

        graph = nx.DiGraph()
        for url, title in nodes:
            graph.add_node(url, title=title or url, label=title or url)
        for src, dst in edges:
            if src and dst:
                graph.add_edge(src, dst)

        net = Network(height="750px", width="100%", directed=True, notebook=False, bgcolor="#222222", font_color="white", filter_menu=True)
        net.from_nx(graph)
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "stabilization": {
              "enabled": true,
              "iterations": 200,
              "fit": true
            }
          },
          "layout": {
            "improvedLayout": true
          },
          "interaction": {
            "hover": true
          }
        }
        """)

        # Ensure labels fall back to id/title for readability and add hover title with page title + URL
        for node in net.nodes:
            label = node.get("label") or node.get("title") or node.get("id")
            url = node.get("id")
            title = node.get("title") or label
            node["label"] = label
            node["title"] = f"{title}<br/>{url}" if url else title

        html_path = os.path.join(export_path, f"{prefix}_graph.html")
        net.write_html(html_path)
        if self.verbose:
            print(f"## Visualization created at: {html_path}")
