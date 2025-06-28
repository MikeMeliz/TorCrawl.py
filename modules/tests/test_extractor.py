import os.path
import unittest
from unittest import mock

from modules.extractor import (
    text,
    check_yara,
    input_file_to_folder,
    input_file_to_terminal,
    url_to_folder,
    url_to_terminal,
    extractor
)


class TestExtractorFunctions(unittest.TestCase):
    @classmethod
    def setUp(cls) -> None:
        """ Test Suite Setup. """
        # Setup activities before each test.

    @classmethod
    def tearDownClass(cls):
        """ Test Suite Teardown. """
        # Remove test files or folders created during tests.
        if os.path.exists('output/torcrawl'):
            os.rmdir('output/torcrawl')

    @mock.patch('requests.get')
    def test_text(self, mock_get):
        """ text unit test.
        Returns true if the function processes a text input correctly.
        """
        self.assertEqual(len(mock_get.call_args_list), 3)
        self.assertIn(mock.call('http://someurl.com/test.json'), mock_get.call_args_list)

        input_data = "test input"
        expected = "expected output"
        result = text(input_data)
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

    def test_check_yara(self):
        """ check_yara unit test.
        Returns true if YARA rules are validated correctly.
        """
        valid_yara_rule = "rule ExampleRule { condition: true }"
        invalid_yara_rule = "invalid rule format"

        # Test valid rule
        expected = "expected output for valid rule"
        result = check_yara(valid_yara_rule)
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

        # Test invalid rule
        with self.assertRaises(Exception):
            check_yara(invalid_yara_rule)

    def test_input_file_to_folder(self):
        """ input_file_to_folder unit test.
        Returns true if files are moved to folders correctly.
        """
        file_path = "path/to/valid_file"
        folder_path = "path/to/valid_folder"

        result = input_file_to_folder(file_path, folder_path)
        expected = "expected output"
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

        # Test with invalid file path
        invalid_file_path = "path/to/nonexistent_file"
        with self.assertRaises(FileNotFoundError):
            input_file_to_folder(invalid_file_path, folder_path)

    def test_input_file_to_terminal(self):
        """ input_file_to_terminal unit test.
        Verifies if file content is printed to the terminal successfully.
        """
        file_path = "path/to/valid_file"

        result = input_file_to_terminal(file_path)
        expected = "expected terminal output"
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

        # Test with invalid file path
        invalid_file_path = "path/to/nonexistent_file"
        with self.assertRaises(FileNotFoundError):
            input_file_to_terminal(invalid_file_path)

    @mock.patch('requests.get')
    def test_url_to_folder(self, mock_get):
        """ url_to_folder unit test.
        Ensures content is downloaded from URL to folder correctly.
        """
        url = "http://valid.url"
        folder_path = "path/to/valid_folder"

        result = url_to_folder(url, folder_path)
        expected = "expected output"
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

        # Test with invalid URL
        mock_get.side_effect = Exception("Invalid URL")
        with self.assertRaises(Exception):
            url_to_folder("invalid_url", folder_path)

    @mock.patch('requests.get')
    def test_url_to_terminal(self, mock_get):
        """ url_to_terminal unit test.
        Ensures content is displayed from URL to terminal correctly.
        """
        url = "http://valid.url"

        result = url_to_terminal(url)
        expected = "expected terminal output"
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

        # Test with invalid URL
        mock_get.side_effect = Exception("Invalid URL")
        with self.assertRaises(Exception):
            url_to_terminal("invalid_url")

    def test_extractor(self):
        """ extractor unit test.
        Ensures extractor function behaves as expected with valid inputs.
        """
        input_data = "valid input"

        result = extractor(input_data)
        expected = "expected output"
        self.assertEqual(expected, result,
                         f'Test Fail:: expected = {expected}, got {result}')

        # Test with invalid input
        invalid_input = "invalid input"
        with self.assertRaises(Exception):
            extractor(invalid_input)
