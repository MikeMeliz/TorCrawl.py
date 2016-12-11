<!--
  Title: TorCrawl.py
  Description: a python script to crawl and extract (regular or onion) webpages through TOR network. 
  Author: MikeMeliz
  -->
  
# TorCrawl.py

## Basic Information:
TorCrawl.py is a python script to crawl and extract (regular or onion) webpages through TOR network. 

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
-v  |--verbose| Verbose output 
-u  |--url | URL of Webpage
-w  |--without| Without the use of TOR
-o  |--output| Output to File
**Extract**: | | 
-e  |--extract| Extract page's code to terminal or file. 
-i  |~~--input~~| ~~Input file with URL(s)~~
-o  |--output| Output page(s) to file(s)
**Crawl**: | |
-c  |--crawl| Crawl website
-d  |--cdepth| Set depth of crawl's travel (1-5)
-z  |~~--exclusions~~| ~~Paths that you don't want to include~~
-s  |~~--simultaneous~~| ~~How many pages to visit at the same time~~
-p  |--pause| The length of time the crawler will pause
-l  |~~--log~~| ~~A save log will let you see which URLs were visited~~
*every argument with overline is still in development*

## Usage:

### As Extractor:
To just extract a single webpage to terminal:

```
python torcrawl.py -u http://www.github.com
<!DOCTYPE html>
...
</html>
```

Extract into a file (github.htm) without the use of TOR

```
python torcrawl.py -w -u http://www.github.com -o github.htm
## File created on /script/path/github.htm
```

Extract to terminal and find only the line with google-analytics

```
python torcrawl.py -u http://www.github.com | grep 'google-analytics'
    <meta name="google-analytics" content="UA-3769691-2">
```

### As Crawler:
Crawl the links of the webpage without the use of TOR,
also show verbose output (really helpfull)

```
python torcrawl.py -v -w -u http://www.github.com -c
## URL: http://www.github.com
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com with step 1 and wait 0
## Step 1 completed with: 11 results
## File created on /script/path/links.txt
```

Crawl the webpage with depth 2 (2 clicks) and 5 seconds waiting before crawl the next page

```
python torcrawl.py -v -u http://www.github.com -c -d 2 -p 5
## URL: http://www.github.com
## Your IP: *.*.*.*
## Crawler Started from http://www.github.com with step 2 and wait 5
## Step 1 completed with: 11 results
## Step 2 completed with: 112 results
## File created on /script/path/links.txt
```

## Contributors:
Feel free to contribute on this project! Just fork it, make any change on your fork and add a pull request on current branch! Any advice, help or questions will be great for me :)

## License:
“GPL” stands for “General Public License”. Using the GNU GPL will require that all the released improved versions be free software. [source & more](https://www.gnu.org/licenses/gpl-faq.html)
