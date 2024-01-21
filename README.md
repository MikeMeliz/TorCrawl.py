<!--
  Title: TorCrawl.py
  Description: a python script to crawl and extract (regular or onion) webpages through TOR network. 
  Author: MikeMeliz
  -->
# TorCrawl.py

[![Version](https://img.shields.io/badge/version-1.2-green.svg?style=plastic)]() [![Python](https://img.shields.io/badge/python-v3-blue.svg?style=plastic)]() [![license](https://img.shields.io/github/license/MikeMeliz/TorCrawl.py.svg?style=plastic)]()

## Basic Information:
TorCrawl.py is a python script to crawl and extract (regular or onion) webpages through TOR network. 

- **Warning:** Crawling is not illegal, but violating copyright is. It’s always best to double check a website’s T&C before crawling them. Some websites set up what’s called robots.txt to tell crawlers not to visit those pages. This crawler will allow you to go around this, but we always recommend respecting robots.txt.
- **Keep in mind:** Extracting and crawling through TOR network take some time. That's normal behaviour; you can find more information [here](https://www.torproject.org/docs/faq.html.en#WhySlow). 

<p align="center"><img src ="https://media.giphy.com/media/RmfzOLuCJTApa/giphy.gif"></p>

### What makes it simple?

If you are a terminal maniac you know that things have to be simple and clear. Passing output into other tools is necessary and accuracy is the key.

With a single argument you can read an .onion webpage or a regular one through TOR Network and using pipes you can pass the output at any other tool you prefer.

```shell
$ torcrawl -u http://www.github.com/ | grep 'google-analytics'
    <meta-name="google-analytics" content="UA-XXXXXX- "> 
```

If you want to crawl the links of a webpage use the `-c` and **BAM** you got on a file all the inside links. You can even use `-d` to crawl them and so on. As far, there is also the necessary argument `-p` to wait some seconds before the next crawl.

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

## Installation:
To install this script, you need to clone that repository:

`git clone https://github.com/MikeMeliz/TorCrawl.py.git`

You'll also need to install dependecies:

`pip install -r requirements.txt`

Of course, the TOR Hidden Service is needed:

Debian/Ubuntu: `apt-get install tor`
[(for more distros and instructions)](https://www.torproject.org/docs/)

## Arguments:
arg | Long | Description
----|------|------------
**General**: | |
-h  |--help| Help
-v  |--verbose| Show more informations about the progress 
-u  |--url *.onion| URL of Webpage to crawl or extract
-w  |--without| Without the use of Relay TOR
-f  |--folder| The directory which will contain the generated files ([@guyo13](https://www.github.com/guyo13))
**Extract**: | | 
-e  |--extract| Extract page's code to terminal or file (Default: Terminal)
-i  |--input filename| Input file with URL(s) (seperated by line)
-o  |--output [filename]| Output page(s) to file(s) (for one page)
-y  |--yara | Perform yara keyword search <br>h = search entire html object,<br>t = search only text <br>([@the-siegfried](https://github.com/the-siegfried))
**Crawl**: | |
-c  |--crawl| Crawl website (Default output on /links.txt)
-d  |--cdepth| Set depth of crawl's travel (Default: 1)
-p  |--pause| The length of time the crawler will pause (Default: 0)
-l  |--log| Log file with visited URLs and their response code

## Usage:

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
Crawl the links of the webpage without the use of TOR,
also show verbose output (really helpfull):

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

## Demo:
![peek 2018-12-08 16-11](https://user-images.githubusercontent.com/9204902/49687660-f72f8280-fb0e-11e8-981e-1bbeeac398cc.gif)

## Contributors:
Feel free to contribute on this project! Just fork it, make any change on your fork and add a pull request on current branch! Any advice, help or questions would be appreciated :shipit:

## License:
“GPL” stands for “General Public License”. Using the GNU GPL will require that all the released improved versions be free software. [source & more](https://www.gnu.org/licenses/gpl-faq.html)

## Changelog:
```
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
