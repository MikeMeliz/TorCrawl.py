#!/usr/bin/python
"""
TorCrawl.py is a python script to crawl and extract (regular or onion)
webpages through TOR network.

usage: python torcrawl.py [options]
python torcrawl.py -u l0r3m1p5umD0lorS1t4m3t.onion
python torcrawl.py -v -w -u http://www.github.com -o github.htm
python torcrawl.py -v -u l0r3m1p5umD0lorS1t4m3t.onion -c -d 2 -p 5
python torcrawl.py -v -w -u http://www.github.com -c -d 2 -p 5 -e -f GitHub

General:
-h, --help         : Help
-v, --verbose      : Show more information about the progress
-u, --url *.onion  : URL of Webpage to crawl or extract
-w, --without      : Without the use of Relay TOR
-rua, --random-ua  : Enable random user-agent rotation for requests
-rpr, --random-proxy: Enable random proxy rotation from res/proxies.txt
-px, --proxy       : IP address for SOCKS5 proxy
-pr, --proxyport   : Port for SOCKS5 proxy
-V, --version      : Show version and exit

Extract:
-e, --extract           : Extract page's code to terminal or file.
                          (Default: terminal)
-i, --input filename    : Input file with URL(s) (separated by line)
-o, --output [filename] : Output page(s) to file(s) (for one page)
-y, --yara              : Yara keyword search page categorisation
                            read in from /res folder. 
                            'h' search whole html object.
                            't' search only the text.

Crawl:
-c, --crawl       : Crawl website (Default output on /links.txt)
-d, --depth       : Set depth of crawl's travel (Default: 1)
-p, --pause       : The length of time the crawler will pause (Default: 0)
-f, --folder      : The directory which will contain the generated files
-j, --json        : Export crawl findings to JSON in addition to txt outputs
-x, --xml         : Export crawl findings to XML in addition to txt outputs
-DB, --database   : Export crawl findings and link graph to SQLite database
-vis, --visualization: Generate HTML visualization (requires -DB)
-l, --log         : Log file with visited URLs and their response code.

GitHub: github.com/MikeMeliz/TorCrawl.py
License: GNU General Public License v3.0

"""

from torcrawl.cli import main

# Stub to call main method.
if __name__ == "__main__":
    main()