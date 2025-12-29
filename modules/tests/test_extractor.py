import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

import modules.extractor as extractor_mod
from modules.extractor import (
    text,
    check_yara,
    input_file_to_folder,
    input_file_to_terminal,
    url_to_folder,
    url_to_terminal,
    extractor,
)


class TestExtractorFunctions(unittest.TestCase):
    def test_text_strips_scripts_and_styles(self):
        html = "<html><head><style>.x{}</style></head><body>Hello<script>ignored()</script><p>World</p></body></html>"
        self.assertEqual("Hello World", text(html))

    def test_check_yara_returns_matches_and_uses_text_mode(self):
        fake_yara = mock.Mock()
        rules_mock = mock.Mock()
        rules_mock.match.return_value = ["hit"]
        fake_yara.compile.return_value = rules_mock

        with mock.patch.dict("sys.modules", {"yara": fake_yara}):
            result = check_yara("<html><body>Keyword</body></html>", yara=1)

        self.assertEqual(["hit"], result)
        fake_yara.compile.assert_called_once()
        rules_mock.match.assert_called_once()

    def test_check_yara_returns_none_when_raw_missing(self):
        with mock.patch.dict("sys.modules", {"yara": mock.Mock()}):
            self.assertIsNone(check_yara(None, yara=0))

    def test_input_file_to_folder_writes_files_and_handles_duplicates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "urls.txt")
            urls = [
                "http://example.com/index.htm\n",
                "http://example.com/index.htm\n",
            ]
            with open(input_path, "w", encoding="utf-8") as f:
                f.writelines(urls)

            with mock.patch.object(
                extractor_mod, "_make_request_with_ua", return_value=b"content"
            ):
                input_file_to_folder(input_path, temp_dir, yara=None)

            created = sorted(os.listdir(temp_dir))
            self.assertIn("index.htm", created)
            self.assertIn("index.htm(1)", created)
            for filename in ("index.htm", "index.htm(1)"):
                with open(os.path.join(temp_dir, filename), "rb") as f:
                    self.assertEqual(b"content", f.read())

    def test_input_file_to_terminal_prints_content_and_no_matches(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            temp_file.write("example.com\n")
            temp_file_path = temp_file.name
        self.addCleanup(lambda: os.remove(temp_file_path))

        with mock.patch.object(
            extractor_mod, "_make_request_with_ua", return_value=b"body"
        ), mock.patch.object(extractor_mod, "check_yara", return_value=[]):
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                input_file_to_terminal(temp_file_path, yara=1, random_ua=False, random_proxy=False)

        output = buffer.getvalue()
        self.assertIn("No matches in:", output)

    def test_url_to_folder_writes_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.object(
                extractor_mod, "_make_request_with_ua", return_value=b"data"
            ), mock.patch.object(extractor_mod, "check_yara", return_value=[]):
                url_to_folder("http://example.com", "out.html", temp_dir, yara=1)

            target = os.path.join(temp_dir, "out.html")
            self.assertTrue(os.path.exists(target))
            with open(target, "rb") as f:
                self.assertEqual(b"data", f.read())

    def test_url_to_terminal_prints_content(self):
        with mock.patch.object(
            extractor_mod, "_make_request_with_ua", return_value=b"payload"
        ), mock.patch.object(extractor_mod, "check_yara", return_value=["match"]):
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                url_to_terminal("http://example.com", yara=1)

        self.assertIn("payload", buffer.getvalue())

    def test_extractor_routes_to_input_file_to_folder(self):
        with mock.patch.object(extractor_mod, "input_file_to_folder") as to_folder, \
             mock.patch.object(extractor_mod, "input_file_to_terminal") as to_terminal, \
             mock.patch.object(extractor_mod, "url_to_folder") as url_to_fold, \
             mock.patch.object(extractor_mod, "url_to_terminal") as url_to_term:

            extractor(
                website="http://example.com",
                crawl=True,
                output_file="",
                input_file="input.txt",
                output_path="out",
                selection_yara=1,
            )

            to_folder.assert_called_once()
            to_terminal.assert_not_called()
            url_to_fold.assert_not_called()
            url_to_term.assert_not_called()

    def test_extractor_routes_to_url_to_terminal_when_no_files(self):
        with mock.patch.object(extractor_mod, "url_to_terminal") as url_to_term:
            extractor(
                website="http://example.com",
                crawl=False,
                output_file="",
                input_file="",
                output_path="out",
                selection_yara=1,
            )
            url_to_term.assert_called_once()
