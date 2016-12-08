# TorCrawl.py

##Basic Information:
TorCrawl.py is a simple python -terminal based- script
to crawl webpage through TOR. 
It's created in that way that you can use grep to search
on the page.

##Examples:
`./torcrawl.py -u http://www.github.com `

`./torcrawl.py -v -w -u http://www.github.com -o github.htm `

`./torcrawl.py -u http://www.github.com | grep 'google-analytics'`


##Arguments:
arg | Long | Description
----|------|------------
-h  |--help| Help
-v  |--verbose| Show steps
-u  |--url | URL of Webpage
-w  |--without| Without the us of TOR
-o  |--output| Output to File
