import os.path
import unittest

from modules.checker import extract_domain
from modules.checker import folder
from modules.checker import url_canon


class TestCheckFunctions(unittest.TestCase):
    @classmethod
    def setUp(cls) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        """ Test Suite Teardown. """
        # Remove test folder.
        os.rmdir('output/torcrawl')

    def test_url_canon_001(self):
        """ url_canon unit test.
        Returns true if the function successfully adds 'https://'.
        """
        url = 'torcrawl.com'
        expected = 'https://torcrawl.com'
        result = url_canon(url, False)
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

    def test_url_canon_002(self):
        """ url_canon unit test.
        Returns true if the function successfully adds 'https://' over `www.`.
        """
        url = 'www.torcrawl.com'
        expected = 'https://www.torcrawl.com'
        result = url_canon(url, False)
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

    def test_url_canon_003(self):
        """ url_canon unit test.
        Returns true if the function doesn't change `http://`.
        """
        url = 'http://www.torcrawl.com'
        expected = 'http://www.torcrawl.com'
        result = url_canon(url, False)
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

    def test_url_canon_004(self):
        """ url_canon unit test.
        Returns true if the function doesn't change `https://`.
        """
        url = 'https://www.torcrawl.com'
        expected = 'https://www.torcrawl.com'
        result = url_canon(url, False)
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

    def test_extract_domain_001(self):
        """ extract_domain test.
         Returns true if correct domain is returned.
        """
        url = 'http://www.torcrawl.com/test/domain-extract/api?id=001'
        expected = 'www.torcrawl.com'
        result = extract_domain(url, True)
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

    def test_extract_domain_002(self):
        """ extract_domain test.
         Returns true if correct domain is returned.
        """
        url = 'http://www.torcrawl.com/test/domain-extract/api?id=002'
        expected = 'http://www.torcrawl.com'
        result = extract_domain(url, False)
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

    def test_folder_creation(self):
        """ folder creation test.
         Returns true if folder is successfully created.
        """
        _input = 'torcrawl'
        result = folder(_input, False)
        self.assertTrue(os.path.exists(result),
                        f'Test Fail:: could not find folder {_input}')

    # TODO: Implement check_tor and check_ip tests.
