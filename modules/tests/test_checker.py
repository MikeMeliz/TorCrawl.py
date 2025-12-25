import os.path
import unittest

from modules.checker import extract_domain
from modules.checker import folder
from modules.checker import url_canon
from modules.checker import get_random_user_agent


class TestCheckFunctions(unittest.TestCase):
    @classmethod
    def setUp(cls) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        """ Test Suite Teardown. """
        # Remove test folder if it exists.
        test_folder = 'output/torcrawl'
        if os.path.exists(test_folder):
            os.rmdir(test_folder)

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

    def test_get_random_user_agent_001(self):
        """ get_random_user_agent test.
        Returns true if the function returns a valid user-agent string.
        """
        result = get_random_user_agent()
        self.assertIsNotNone(result,
                            'Test Fail:: get_random_user_agent returned None')
        self.assertIsInstance(result, str,
                             f'Test Fail:: expected str, got {type(result)}')
        self.assertGreater(len(result), 0,
                          'Test Fail:: user-agent string is empty')

    def test_get_random_user_agent_002(self):
        """ get_random_user_agent test.
        Returns true if the returned user-agent contains expected browser identifiers.
        """
        result = get_random_user_agent()
        self.assertIsNotNone(result,
                            'Test Fail:: get_random_user_agent returned None')
        # Check that it contains common browser identifiers
        has_browser = any(browser in result for browser in 
                         ['Mozilla', 'Chrome', 'Safari', 'Firefox', 'Edg', 'OPR'])
        self.assertTrue(has_browser,
                       f'Test Fail:: user-agent does not contain browser identifier: {result}')

    def test_get_random_user_agent_003(self):
        """ get_random_user_agent test.
        Returns true if the function returns different user-agents (randomness test).
        Note: This test may occasionally fail due to randomness, but probability is very low.
        """
        results = []
        # Get 10 random user-agents
        for _ in range(10):
            ua = get_random_user_agent()
            self.assertIsNotNone(ua, 'Test Fail:: get_random_user_agent returned None')
            results.append(ua)
        
        # Check that at least some are different (with 50+ user-agents, very likely)
        unique_results = set(results)
        self.assertGreater(len(unique_results), 1,
                          f'Test Fail:: all user-agents were identical: {results}')

    def test_get_random_user_agent_004(self):
        """ get_random_user_agent test.
        Returns true if the user-agent follows expected format (starts with Mozilla).
        """
        result = get_random_user_agent()
        self.assertIsNotNone(result,
                            'Test Fail:: get_random_user_agent returned None')
        self.assertTrue(result.startswith('Mozilla/'),
                       f'Test Fail:: user-agent does not start with Mozilla/: {result}')

    # TODO: Implement check_tor and check_ip tests.
