import io
import os.path
import socket
import unittest
from unittest import mock

from modules import checker
from modules.checker import extract_domain
from modules.checker import folder
from modules.checker import url_canon
from modules.checker import get_random_user_agent
from modules.checker import get_random_proxy
from modules.checker import check_tor
from modules.checker import check_ip
from modules.checker import setup_proxy_connection


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

    def test_get_random_proxy_001(self):
        """ get_random_proxy test.
        Returns true if the function handles empty proxy file gracefully.
        Note: This test expects proxies.txt to be empty initially.
        """
        # When proxies.txt is empty, function should return None
        # and display helpful message (we can't easily test the message output)
        result = get_random_proxy()
        # Since proxies.txt is empty, result should be None
        # This is expected behavior when no proxies are configured
        self.assertIsNone(result,
                         'Test Fail:: get_random_proxy should return None when no proxies available')

    def test_get_random_proxy_002(self):
        """ get_random_proxy test.
        Returns true if the function can load and return proxies from file.
        This test requires proxies.txt to have at least one proxy entry.
        """
        import os
        proxies_file = os.path.join('res', 'proxies.txt')
        
        # Check if file exists and has content
        if os.path.exists(proxies_file):
            with open(proxies_file, 'r', encoding='UTF-8') as f:
                has_proxies = bool([line.strip() for line in f if line.strip()])
            
            if has_proxies:
                result = get_random_proxy()
                self.assertIsNotNone(result,
                                    'Test Fail:: get_random_proxy returned None when proxies exist')
                self.assertIsInstance(result, str,
                                     f'Test Fail:: expected str, got {type(result)}')
                self.assertGreater(len(result), 0,
                                  'Test Fail:: proxy string is empty')
                # Check format: should contain colon (host:port)
                self.assertIn(':', result,
                             f'Test Fail:: proxy should be in format host:port, got {result}')

    def test_get_random_proxy_003(self):
        """ get_random_proxy test.
        Returns true if the function returns different proxies (randomness test).
        Note: This test requires proxies.txt to have multiple proxy entries.
        """
        import os
        proxies_file = os.path.join('res', 'proxies.txt')
        
        if os.path.exists(proxies_file):
            with open(proxies_file, 'r', encoding='UTF-8') as f:
                proxy_count = len([line.strip() for line in f if line.strip()])
            
            if proxy_count > 1:
                results = []
                # Get 10 random proxies
                for _ in range(10):
                    proxy = get_random_proxy()
                    if proxy:
                        results.append(proxy)
                
                if len(results) > 1:
                    # Check that at least some are different
                    unique_results = set(results)
                    self.assertGreater(len(unique_results), 1,
                                      f'Test Fail:: all proxies were identical: {results}')

    def test_get_random_proxy_004(self):
        """ get_random_proxy test.
        Returns true if the proxy follows expected format (host:port).
        """
        import os
        proxies_file = os.path.join('res', 'proxies.txt')
        
        if os.path.exists(proxies_file):
            with open(proxies_file, 'r', encoding='UTF-8') as f:
                has_proxies = bool([line.strip() for line in f if line.strip()])
            
            if has_proxies:
                result = get_random_proxy()
                if result:
                    # Should be in format host:port
                    parts = result.split(':')
                    self.assertEqual(len(parts), 2,
                                    f'Test Fail:: proxy should be in format host:port, got {result}')
                    # Port should be numeric
                    try:
                        port = int(parts[1])
                        self.assertGreater(port, 0,
                                          f'Test Fail:: port should be positive, got {port}')
                        self.assertLessEqual(port, 65535,
                                            f'Test Fail:: port should be <= 65535, got {port}')
                    except ValueError:
                        self.fail(f'Test Fail:: port should be numeric, got {parts[1]}')
    
    def test_check_tor_reports_running(self):
        with mock.patch("subprocess.check_output", return_value=b"tor\n"):
            # Should not raise when tor string present
            check_tor(verbose=True)

    def test_check_tor_exits_when_missing(self):
        with mock.patch("subprocess.check_output", return_value=b""), \
             mock.patch("sys.exit", side_effect=SystemExit) as exit_mock:
            with self.assertRaises(SystemExit):
                check_tor(verbose=False)
            exit_mock.assert_called_once_with(2)

    def test_check_ip_prints_ip(self):
        fake_response = io.StringIO('{"ip": "1.2.3.4"}')
        with mock.patch("modules.checker.urlopen", return_value=fake_response), \
             mock.patch("modules.checker.load", return_value={"ip": "1.2.3.4"}):
            check_ip()

    def test_setup_proxy_connection_invalid_format(self):
        # Should not throw on malformed string
        with mock.patch.dict("sys.modules", {"socks": mock.Mock()}), \
             mock.patch("modules.checker.socket") as socket_mock:
            setup_proxy_connection("badformat")
            socket_mock.socket.assert_not_called()

    def test_setup_proxy_connection_configures_socket(self):
        fake_socks = mock.Mock()
        fake_socks.socksocket = mock.Mock()
        fake_socks.PROXY_TYPE_SOCKS5 = object()
        # Patch socket attributes so any monkey-patching done by the code is
        # cleaned up automatically at context exit.
        with mock.patch.dict("sys.modules", {"socks": fake_socks}), \
             mock.patch.object(socket, "socket"), \
             mock.patch.object(socket, "getaddrinfo"):
            setup_proxy_connection("host:9050")
        fake_socks.setdefaultproxy.assert_called_once()
