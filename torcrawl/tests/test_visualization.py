import os
import shutil
import unittest

from torcrawl.crawler import Crawler
from torcrawl.checker import url_canon, extract_domain, folder
from torcrawl.export import export_database
from torcrawl.visualization import export_visualization


class TestVisualization(unittest.TestCase):
    def setUp(self):
        _website = url_canon('torcrawl.com', False)
        self.out_path = folder(extract_domain(_website), False)
        self.crawler = Crawler(_website, 0, 1, self.out_path, False, False)

    def tearDown(self):
        shutil.rmtree(self.out_path)

    def test_export_visualization_creates_html(self):
        prefix = f"{self.crawler.timestamp}_results_test_vis"
        self.crawler.findings["links"].update({"https://torcrawl.com", "https://torcrawl.com/about"})
        self.crawler.edges.add(("https://torcrawl.com", "https://torcrawl.com/about"))
        self.crawler.titles["https://torcrawl.com"] = "Home"
        self.crawler.titles["https://torcrawl.com/about"] = "About"

        payload = self.crawler.export_payload()
        export_database(self.out_path, prefix, payload["data"], payload["edges"], payload["titles"], payload["resources"], verbose=False)
        export_visualization(self.out_path, prefix, payload["start_url"], verbose=False)

        html_path = os.path.join(self.out_path, f"{prefix}_graph.html")
        self.assertTrue(os.path.exists(html_path))
        with open(html_path, "r", encoding="utf-8") as html_file:
            contents = html_file.read()
        self.assertIn("<html", contents.lower())


if __name__ == '__main__':
    unittest.main()

