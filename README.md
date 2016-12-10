# TorCrawl.py

## Basic Information:
TorCrawl.py is a python script to crawl and extract webpages through 
TOR network. 

## Examples:
`python torcrawl.py -u http://www.github.com`

`python torcrawl.py -v -w -u http://www.github.com -o github.htm` 

`python torcrawl.py -u http://www.github.com | grep 'google-analytics'`

`python torcrawl.py -v -w -u http://www.github.com -c`

## Arguments:
arg | Long | Description
----|------|------------
General: | |
-h  |--help| Help
-v  |--verbose| Verbose output 
-u  |--url | URL of Webpage
-w  |--without| Without the use of TOR
-o  |--output| Output to File
Extract: | | 
-e  |--extract| Extract page's code to terminal or file. 
-i  |~~--input~~| Input file with URL(s)
-o  |--output| Output page(s) to file(s)
Crawl: | |
-c  |--crawl| Crawl website
-d  |~~--cdepth~~| Set depth of crawl's travel (1-5)
-e  |~~--exclusions~~| Paths that you don't want to include
-s  |~~--simultaneous~~| How many pages to visit at the same time
-p  |~~--pause~~| The length of time the crawler will pause
-l  |~~--log~~| A save log will let you see which URLs were visited
*every long argument with overline is still in development*

## Contributors:
Feel free to contribute on this project! Just fork it, make any change on your fork and add a pull request on current branch! Any advice, help or questions will be great for me :)

## License:
“GPL” stands for “General Public License”. Using the GNU GPL will require that all the released improved versions be free software. [source](https://www.gnu.org/licenses/gpl-faq.html)
