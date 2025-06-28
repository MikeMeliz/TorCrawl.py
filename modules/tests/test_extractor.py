import os.path
import unittest
from unittest import mock

from modules.extractor import text

class TestExtractorFunctions(unittest.TestCase):
    @classmethod
    def setUp(cls) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        """ Test Suite Teardown. """
        # Remove test folder.
        os.rmdir('output/torcrawl')

    @mock.patch('requests.get')
    def test_text(self, mock_get):
        """ text unit test.
        Returns true if the function successfully fetch text out of a website.
        """
        self.assertEqual(len(mock_get.call_args_list), 3)
        self.assertIn(mock.call('http://someurl.com/test.json'), mock_get.call_args_list)

        url = 'torcrawl.com'
        expected = 'https://torcrawl.com'
        result = url_canon(url, False)
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')