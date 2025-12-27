import shutil
import tempfile
import unittest
from unittest import mock
import urllib.request

from modules.crawler import Crawler
from modules.checker import url_canon
from modules.checker import extract_domain
from modules.checker import folder


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
                 [f'bob.html', f'{_uri}bob.html']]

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

    def test_make_request_with_random_ua_and_proxy(self):
        crawler = Crawler("http://example.com", 0, 0, self.out_path, False, False, random_ua=True, random_proxy=True)
        with mock.patch("modules.crawler.get_random_proxy", return_value="proxy:9050") as proxy_mock, \
             mock.patch("modules.crawler.setup_proxy_connection") as setup_mock, \
             mock.patch("modules.crawler.get_random_user_agent", return_value="UA") as ua_mock, \
             mock.patch("modules.crawler.urllib.request.urlopen") as urlopen_mock:
            crawler._make_request("http://example.com")
        proxy_mock.assert_called_once()
        setup_mock.assert_called_once_with("proxy:9050")
        req_arg = urlopen_mock.call_args[0][0]
        self.assertIsInstance(req_arg, urllib.request.Request)
        # urllib stores header keys normalized to title-case "User-agent"
        self.assertEqual(req_arg.get_header("User-agent"), "UA")

    def test_make_request_without_randoms(self):
        crawler = Crawler("http://example.com", 0, 0, self.out_path, False, False, random_ua=False, random_proxy=False)
        with mock.patch("modules.crawler.urllib.request.urlopen") as urlopen_mock:
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
