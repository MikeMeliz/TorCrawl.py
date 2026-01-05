import os
import shutil
import tempfile
import unittest
import datetime
from unittest.mock import patch
from unittest import mock
import urllib.request
import json
import sqlite3
import xml.etree.ElementTree as ET

from torcrawl.crawler import Crawler
from torcrawl.checker import url_canon
from torcrawl.checker import extract_domain
from torcrawl.checker import folder


class TestCrawlerFunctions(unittest.TestCase):
    def setUp(self):
        _website = url_canon('torcrawl.com', False)
        self.out_path = out_path = folder(extract_domain(_website), False)
        self.crawler = Crawler(_website, 0, 1, out_path, False, False)

    def tearDown(self):
        """ Test Suite Teardown. """
        # Remove test folder.
        shutil.rmtree(self.out_path)

    def test_excludes(self):
        """ Test crawler.excludes function.
        Return True if the function successfully excludes the provided failing links.
        """
        _uri = 'http://www.torcrawl.com'
        failing_links = ['#', 'tel:012-013-104-5',
                         'mailto:test@torcrawl.com', f'{_uri}/res/test.pdf',
                         f'{_uri}/res/test.doc', f'{_uri}/res/test.jpg',
                         f'{_uri}/res/test.png', f'{_uri}/res/test.jpeg',
                         f'{_uri}/res/test.gif']
        for link in failing_links:
            self.assertTrue(self.crawler.excludes(link),
                            f'Test Fail:: Link: {link} - not excluded')

    def test_canonical(self):
        """ Test crawler.canonical function.
        Return True if the function successfully normalizes the provided
        failing links.
        """
        _uri = 'https://torcrawl.com/'
        links = [[f'{_uri}sundance', f'{_uri}sundance'],
                 ['/sundance', f'{_uri}sundance'],
                 [f'{_uri}bob.html', f'{_uri}bob.html'],
                 [f'bob.html', f'{_uri}bob.html'],
                 ['about', f'{_uri}about'],
                 ['services/', f'{_uri}services/']]

        for link in links:
            result = self.crawler.canonical(link[0])
            self.assertEqual(link[1], result,
                             f'Test Fail:: Canon returned = {result}, '
                             f'expected {link[1]}')

    def test_crawl(self):
        """ Test Crawlwer.crawl functionality"""
        # TODO: Test Crawler.crawl against live web application.
        # Re-instantiate crawler with live application.
        pass

    def test_excludes_writes_images_file(self):
        """Image links are excluded and logged to _images.txt."""
        now = self.crawler.timestamp
        img_link = 'https://torcrawl.com/res/test-image.png'
        self.assertTrue(self.crawler.excludes(img_link))

        img_file = f"{self.out_path}/{now}_images.txt"
        with open(img_file, 'r', encoding='UTF-8') as f:
            contents = f.read()
        self.assertIn(img_link, contents)

    def test_excludes_writes_scripts_file(self):
        """Script links are excluded and logged to _scripts.txt."""
        now = self.crawler.timestamp
        script_link = 'https://torcrawl.com/static/app.js'
        self.assertTrue(self.crawler.excludes(script_link))

        scripts_file = f"{self.out_path}/{now}_scripts.txt"
        with open(scripts_file, 'r', encoding='UTF-8') as f:
            contents = f.read()
        self.assertIn(script_link, contents)

    @patch.object(Crawler, "_make_request")
    def test_crawl_regex_finds_plain_urls(self, mock_request):
        """Ensure regex fallback finds URLs not wrapped in <a>/<area> tags."""
        html = b"""
        <html><body>
        This page mentions https://torcrawl.com/hidden-page without a link tag.
        </body></html>
        """

        class FakeResponse:
            status = 200

            def read(self_inner):
                return html

        mock_request.return_value = FakeResponse()

        # Enable at least one crawl step to trigger parsing.
        self.crawler.c_depth = 1

        result = self.crawler.crawl()

        self.assertIn("https://torcrawl.com/hidden-page", result)

    @patch.object(Crawler, "_make_request")
    def test_crawl_custom_regex_file_patterns(self, mock_request):
        """Custom regex patterns from default file are applied to discover links."""
        html = b"""
        <html><body>
        Resource reference: /deep/custom-path
        Secondary ref: /deep/second-path
        </body></html>
        """

        class FakeResponse:
            status = 200

            def read(self_inner):
                return html

        mock_request.return_value = FakeResponse()

        with tempfile.NamedTemporaryFile('w+', delete=False, encoding='utf-8') as regex_file:
            regex_file.write(r"/deep/[a-z-]+")
            regex_file_path = regex_file.name

        self.addCleanup(lambda: os.path.exists(regex_file_path) and os.remove(regex_file_path))

        with patch('torcrawl.crawler.DEFAULT_REGEX_FILE', regex_file_path):
            crawler = Crawler(self.crawler.website, 1, 0, self.out_path, False, False)

        result = crawler.crawl()

        self.assertIn("https://torcrawl.com/deep/custom-path", result)
        self.assertIn("https://torcrawl.com/deep/second-path", result)


    def test_make_request_with_random_ua_and_proxy(self):
        crawler = Crawler("http://example.com", 0, 0, self.out_path, False, False, random_ua=True, random_proxy=True)
        with mock.patch("torcrawl.crawler.get_random_proxy", return_value="proxy:9050") as proxy_mock, \
             mock.patch("torcrawl.crawler.setup_proxy_connection") as setup_mock, \
             mock.patch("torcrawl.crawler.get_random_user_agent", return_value="UA") as ua_mock, \
             mock.patch("torcrawl.crawler.urllib.request.urlopen") as urlopen_mock:
            crawler._make_request("http://example.com")
        proxy_mock.assert_called_once()
        setup_mock.assert_called_once_with("proxy:9050")
        req_arg = urlopen_mock.call_args[0][0]
        self.assertIsInstance(req_arg, urllib.request.Request)
        # urllib stores header keys normalized to title-case "User-agent"
        self.assertEqual(req_arg.get_header("User-agent"), "UA")

    def test_make_request_without_randoms(self):
        crawler = Crawler("http://example.com", 0, 0, self.out_path, False, False, random_ua=False, random_proxy=False)
        with mock.patch("torcrawl.crawler.urllib.request.urlopen") as urlopen_mock:
            crawler._make_request("http://example.com")
        urlopen_mock.assert_called_once_with("http://example.com")

    def test_crawl_collects_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            crawler = Crawler("https://example.com", 1, 0, temp_dir, False, False)

            class DummyResponse:
                def __init__(self, body):
                    self.body = body
                    self.status = 200

                def read(self):
                    return self.body

            html = b"<html><a href='/page1'>p</a><a href='mailto:test@example.com'>m</a></html>"
            dummy = DummyResponse(html)

            with mock.patch.object(crawler, "_make_request", return_value=dummy):
                result = crawler.crawl()

            self.assertIn("https://example.com", result)
            self.assertIn("https://example.com/page1", result)
