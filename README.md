<!--
  Title: TorCrawl.py
  Description: A Python script designed for anonymous web scraping via the Tor network. 
  Author: MikeMeliz
  -->

<div align="center">
  
  <img width="50%" alt="TorCrawl.py Logo" src=".github/torcrawl.svg">
  
  ### TorCrawl.py is a Python script designed for anonymous web scraping via the Tor network.
  <p>It combines ease of use with the robust privacy features of Tor, allowing for secure and untraceable data collection. Ideal for both novice and experienced programmers, this tool is essential for responsible data gathering in the digital age.</p>
  
  [![Release][release-version-shield]][releases-link]
  [![Last Commit][last-commit-shield]][commit-link]
  ![Python][python-version-shield]
  [![Quality Gate Status][quality-gate-shield]][quality-gate-link]
  [![license][license-shield]][license-link]

</div>

### What makes it simple and easy to use?

If you are a terminal maniac you know that things have to be simple and clear. Passing the output into other tools is necessary and accuracy is the key.

With a single argument, you can read an .onion webpage or a regular one, through TOR Network and by using pipes you can pass the output at any other tool you prefer.

```shell
$ torcrawl -u http://www.github.com/ | grep 'google-analytics'
    <meta-name="google-analytics" content="UA-XXXXXX- "> 
```

If you want to crawl the links of a webpage use the `-c` and **BAM** you got on a file all the inside links. You can even use `-d` to crawl them and so on. You can also use the argument `-p` to wait some seconds before the next crawl.

```shell
$ torcrawl -v -u http://www.github.com/ -c -d 2 -p 2
# TOR is ready!
# URL: http://www.github.com/
# Your IP: XXX.XXX.XXX.XXX
# Crawler started from http://www.github.com/ with 2 depth crawl and 2 second(s) delay:
# Step 1 completed with: 11 results
# Step 2 completed with: 112 results
# File created on /path/to/project/links.txt
```

> [!TIP]  
> Crawling is not illegal, but violating copyright *is*. It’s always best to double-check a website’s T&C before start crawling them. Some websites set up what’s called `robots.txt` to tell crawlers not to visit those pages.
> <br>This crawler *will* allow you to go around this, but we always *recommend* respecting robots.txt.

<hr>

## Installation

### Easy Installation:
- from [PyPi][pypi-package]:<br>
`pip install torcrawl`
- with homebrew:<br>
*Coming soon...*

### Manual Installation:
1. **Clone this repository**:<br>
`git clone https://github.com/MikeMeliz/TorCrawl.py.git`
2. **Install dependencies**:<br>
`pip install -r requirements.txt`
3. **Install and Start TOR Service**:
    1. **Debian/Ubuntu**: <br>
        `apt-get install tor`<br>
        `service tor start`
    2. **Windows**: Download [`tor.exe`][tor-download], and:<br>
        `tor.exe --service install`<br>
        `tor.exe --service start`
    3. **MacOS**: <br>
        `brew install tor`<br>
        `brew services start tor`
    4. For different distros, visit:<br>
       [TOR Setup Documentation][tor-docs]

## Arguments
| **arg**      | **Long**            | **Description**                                                                        |
|--------------|---------------------|----------------------------------------------------------------------------------------|
| **General**: |                     |                                                                                        |
| -h           | --help              | Help message                                                                           |
| -v           | --verbose           | Show more information about the progress                                               |
| -u           | --url *.onion       | URL of Webpage to crawl or extract                                                     |
| -w           | --without           | Without using TOR Network                                                              |
| -rua         | --random-ua         | Enable random user-agent rotation for requests (works with both TOR and clearnet)     |
| -rpr         | --random-proxy       | Enable random proxy rotation from res/proxies.txt (requires -w flag, one proxy per line, format: host:port) |
| -px          | --proxy             | IP address for SOCKS5 proxy (Default: 127.0.0.1 for using TOR)                         |
| -pr          | --proxyport         | Port for SOCKS5 proxy (Default: 9050)                                                  |
| -f           | --folder            | The directory which will contain the generated files                                   |
| -V           | --version           | Show version and exit                                                                  |
| **Extract**: |                     |                                                                                        |
| -e           | --extract           | Extract page's code to terminal or file (Default: Terminal)                            |
| -i           | --input filename    | Input file with URL(s) (separated by line)                                             |
| -o           | --output [filename] | Output page(s) to file(s) (for one page)                                               |
| -y           | --yara              | Perform yara keyword search:<br>h = search entire html object,<br>t = search only text |
| **Crawl**:   |                     |                                                                                        |
| -c           | --crawl             | Crawl website (Default output on website/links.txt)                                    |
| -d           | --depth             | Set depth of crawler's travel (Default: 1)                                             |
| -p           | --pause             | Seconds of pause between requests (Default: 0)                                         |
| -l           | --log               | Log file with visited URLs and their response code                                     |

## Usage & Examples

### As Extractor:
To just extract a single webpage to terminal:

```shell
$ python torcrawl.py -u http://www.github.com
<!DOCTYPE html>
...
</html>
```

Extract into a file (github.htm) without the use of TOR:

```shell
$ python torcrawl.py -w -u http://www.github.com -o github.htm
## File created on /script/path/github.htm
```

Extract to terminal and find only the line with google-analytics:

```shell
$ python torcrawl.py -u http://www.github.com | grep 'google-analytics'
    <meta name="google-analytics" content="UA-*******-*">
```

Extract to file and find only the line with google-analytics using yara:
```shell
$ python torcrawl.py -v -w -u https://github.com -e -y 0
...
```
**_Note:_** update res/keyword.yar to search for other keywords.
Use ```-y 0``` for raw html searching and ```-y 1``` for text search only.

Extract a set of webpages (imported from file) to terminal:

```shell
$ python torcrawl.py -i links.txt
...
```


### As Crawler:
Crawl the links of the webpage without the use of TOR, also show verbose output (really helpful):

```shell
$ python torcrawl.py -v -w -u http://www.github.com/ -c
## URL: http://www.github.com/
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com/ with step 1 and wait 0
## Step 1 completed with: 11 results
## File created on /script/path/links.txt
```

Crawl the webpage with depth 2 (2 clicks) and 5 seconds waiting before crawl the next page:

```shell
$ python torcrawl.py -v -u http://www.github.com/ -c -d 2 -p 5
## TOR is ready!
## URL: http://www.github.com/
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com with step 2 and wait 5
## Step 1 completed with: 11 results
## Step 2 completed with: 112 results
## File created on /script/path/links.txt
```
### As Both:
You can crawl a page and also extract the webpages into a folder with a single command:

```shell
$ python torcrawl.py -v -u http://www.github.com/ -c -d 2 -p 5 -e
## TOR is ready!
## URL: http://www.github.com/
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com with step 1 and wait 5
## Step 1 completed with: 11 results
## File created on /script/path/FolderName/index.htm
## File created on /script/path/FolderName/projects.html
## ...
```
***Note:*** *The default (and only for now) file for crawler's links is the `links.txt` document. Also, to extract right after the crawl you have to give `-e` argument*

Following the same logic; you can parse all these pages to grep (for example) and search for specific text:

```shell
$ python torcrawl.py -u http://www.github.com/ -c -e | grep '</html>'
</html>
</html>
...
```

### As Both + Keyword Search:
You can crawl a page, perform a keyword search and extract the webpages that match the findings into a folder with a single command:

```shell
$ python torcrawl.py -v -u http://www.github.com/ -c -d 2 -p 5 -e -y h
## TOR is ready!
## URL: http://www.github.com/
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com with step 1 and wait 5
## Step 1 completed with: 11 results
## File created on /script/path/FolderName/index.htm
## File created on /script/path/FolderName/projects.html
## ...
```

***Note:*** *Update res/keyword.yar to search for other keywords.
Use ```-y h``` for raw html searching and ```-y t``` for text search only.*

## Demo
![TorCrawl-Demo][demo]

## Contribution
Feel free to contribute on this project! Just fork it, make any change on your fork and add a pull request on current branch!

<a href="https://github.com/MikeMeliz/TorCrawl.py/graphs/contributors"><img src="https://contrib.rocks/image?repo=MikeMeliz/TorCrawl.py" /></a>

:shipit: Any advice, help or questions will be appreciated! :shipit:

## License
“GPL” stands for “General Public License”. Using the GNU GPL will require that all the released improved versions be free software ([More info][gpl-faq]).

## Changelog
```shell
v1.34:
    * Readiness for PyPi and Homebrew
    * Added --version argument
v1.33:
    * Added User-Agent rotation
    * Implemented Proxy rotation
    * Introduced dependabot
v1.32:
    * Removed 1 second default pause between requests
    * Several improvements on results
    * Improved logs
v1.31:
    * Fixed Input Link NoneType Error
    * Fixed name mismatch  
v1.3:
    * Make yara search optional
v1.21:
    * Fixed typos of delay (-d)
    * Fixed TyperError and IndexError 
v1.2:
    * Migrated to Python3
    * Option to generate log file (-l)
    * PEP8 Fixes
    * Fix double folder generation (http:// domain.com)
```

<hr><p align="center"><img src ="https://media.giphy.com/media/RmfzOLuCJTApa/giphy.gif"></p>

<!-- Links -->
[last-commit-shield]: https://img.shields.io/github/last-commit/MikeMeliz/TorCrawl.py?logo=github&label=Last%20Commit&style=plastic
[release-version-shield]: https://img.shields.io/github/v/release/MikeMeliz/TorCrawl.py?logo=github&label=Release&style=plastic
[python-version-shield]: https://img.shields.io/badge/Python-v3-green.svg?style=plastic&logo=python&label=Python
[quality-gate-shield]: https://sonarcloud.io/api/project_badges/measure?project=MikeMeliz_TorCrawl.py&metric=alert_status
[quality-gate-link]: https://sonarcloud.io/summary/new_code?id=MikeMeliz_TorCrawl.py
[license-shield]: https://img.shields.io/github/license/MikeMeliz/TorCrawl.py.svg?style=plastic&logo=gnu&label=License
[commit-link]: https://github.com/MikeMeliz/TorCrawl.py/commits/main
[releases-link]: https://github.com/MikeMeliz/TorCrawl.py/releases
[license-link]: https://github.com/MikeMeliz/TorCrawl.py/blob/master/LICENSE
[pypi-package]: https://pypi.org/project/torcrawl/
[tor-whyslow]: https://www.torproject.org/docs/faq.html.en#WhySlow
[tor-download]: https://www.torproject.org/download/tor/
[tor-docs]: https://www.torproject.org/docs/
[demo]: https://user-images.githubusercontent.com/9204902/49687660-f72f8280-fb0e-11e8-981e-1bbeeac398cc.gif
[gpl-faq]: https://www.gnu.org/licenses/gpl-faq.html
