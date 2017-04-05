<!--
  Title: TorCrawl.py
  Description: a python script to crawl and extract (regular or onion) webpages through TOR network. 
  Author: MikeMeliz
  -->
# TorCrawl.py

[![Version](https://img.shields.io/badge/version-1.0-green.svg?style=plastic)]() [![license](https://img.shields.io/github/license/MikeMeliz/TorCrawl.py.svg?style=plastic)]()

## Basic Information:
TorCrawl.py is a python script to crawl and extract (regular or onion) webpages through TOR network. 

- **Warning:** Crawling is not illegal, but violating copyright is. It’s always best to double check a website’s T&C before crawling them. Some websites set up what’s called robots.txt to tell crawlers not to visit those pages. This crawler will allow you to go around this, but we always recommend respecting robots.txt.
- **Keep in mind:** Extracting and crawling through TOR network take some time. That's normal behaviour; you can find more information [here](https://www.torproject.org/docs/faq.html.en#WhySlow). 

### What make it simple?

<p align="center"><img src ="https://media.giphy.com/media/RmfzOLuCJTApa/giphy.gif"></p>

If you are a terminal maniac you know that things have to be simple and clear. Passing output into other tools is necessary and accuracy is the key.

With a single argument you can read an .onion webpage or a regular one through TOR Network and using pipes you can pass the output at any other tool you prefer.

![ExtractAndGrep](https://cloud.githubusercontent.com/assets/9204902/21080715/c34511ca-bfbe-11e6-9fec-230e6430d5dc.png)

If you want to crawl the links of a webpage use the `-c` and **BAM** you got on a file all the inside links. You can even use `-d` to crawl them and so on. As far, there is also the necessary argument `-p` to wait some seconds before the next crawl.

![CrawlwDepthwPause](https://cloud.githubusercontent.com/assets/9204902/21080526/f2b80908-bfb9-11e6-8bc0-fd3eebe182cc.png)


## Installation:
To install this script, you need to clone that repository:

`git clone https://github.com/MikeMeliz/TorCrawl.py.git`

You'll also need BeautifulSoup:

`pip install beautifulsoup`

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
**Extract**: | | 
-e  |--extract| Extract page's code to terminal or file. (Default: Terminal)
-i  |--input filename| Input file with URL(s) (seperated by line)
-o  |--output [filename]| Output page(s) to file(s) (for one page)
**Crawl**: | |
-c  |--crawl| Crawl website (Default output on /links.txt)
-d  |--cdepth| Set depth of crawl's travel (Default: 1)
-p  |--pause| The length of time the crawler will pause (Default: 0)
-l  |--log| A save log will let you see which URLs were visited

## Usage:

### As Extractor:
To just extract a single webpage to terminal:

```
$ python torcrawl.py -u http://www.github.com
<!DOCTYPE html>
...
</html>
```

Extract into a file (github.htm) without the use of TOR:

```
$ python torcrawl.py -w -u http://www.github.com -o github.htm
## File created on /script/path/github.htm
```

Extract to terminal and find only the line with google-analytics:

```
$ python torcrawl.py -u http://www.github.com | grep 'google-analytics'
    <meta name="google-analytics" content="UA-*******-*">
```

Extract a set of webpages (imported from file) to terminal:

```
$ python torcrawl.py -i links.txt
...
```


### As Crawler:
Crawl the links of the webpage without the use of TOR,
also show verbose output (really helpfull):

```
$ python torcrawl.py -v -w -u http://www.github.com/ -c
## URL: http://www.github.com/
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com/ with step 1 and wait 0
## Step 1 completed with: 11 results
## File created on /script/path/links.txt
```

Crawl the webpage with depth 2 (2 clicks) and 5 seconds waiting before crawl the next page:

```
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

```
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

With the same logic you can parse all these pages to grep (for example) and search for a specific text:

```
$ python torcrawl.py -u http://www.github.com/ -c -e | grep '</html>'
</html>
</html>
...
```

## Contributors:
Feel free to contribute on this project! Just fork it, make any change on your fork and add a pull request on current branch! Any advice, help or questions will be great for me :)

## License:
“GPL” stands for “General Public License”. Using the GNU GPL will require that all the released improved versions be free software. [source & more](https://www.gnu.org/licenses/gpl-faq.html)
