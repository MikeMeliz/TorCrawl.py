#!/usr/bin/python

help='''
Basic Information:
TorCrawl.py is a python script to crawl and extract (regular or onion)
webpages through TOR network. 

Examples:
python torcrawl.py -u http://www.github.com 
python torcrawl.py -v -w -u http://www.github.com -o github.htm 
python torcrawl.py -u http://www.github.com | grep 'google-analytics'
python torcrawl.py -v -w -u http://www.github.com -c 

General:
-h, --help        : Help
-v, --verbose     : Show steps
-u, --url         : URL of Webpage to crawl or extract
-w, --without     : Without the use of Relay TOR (default ON) 

Extract:
-e, --extract     : Extract page's code to terminal or file.
                    By default, if you don't specify a mode, the
                    script will try to extract the page(s)
-i, --input       : Input file with URL(s)
-o, --output      : Output page(s) to file(s)

Crawl:
-c, --crawl       : Crawl website
-d, --cdepth      : Set depth of crawl's travel (1-5)
-e, --exclusions  : Paths that you don't want to include
-s, --simultaneous: How many pages to visit at the same time
-p, --pause       : The length of time the crawler will pause
-l, --log         : A save log will let you see which URLs were
                    visited
'''

import sys
import os
import getopt
import socket
import socks

# TorCrawl Modules
from modules.crawler import crawler
from modules.extractor import extractor
from modules.checker import *

# Set socket and connection with TOR network
def connectTor():
    try:
      SOCKS_PORT = 9050
      # Set socks proxy and wrap the urllib module
      socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT)
      socket.socket = socks.socksocket
      # Perform DNS resolution through the socket
      def getaddrinfo(*args):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
      socket.getaddrinfo = getaddrinfo
    except:
      e = sys.exc_info()[0]
      print( "Error: %s" % e +"\n## Can't establish connection with TOR")


def main(argv):
    extract = True
    extractarg = False
    verbose = False
    withoutTor = False
    outputToFile = False
    crawl = False
    cdepth = 1
    cpause = 0
    simultaneous = 1
    website = ''
    outputFile = ''
    inputFile = ''

    try:
      opts, args = getopt.getopt(argv,'hvu:wei:o:cd:p:',["help","verbose","url=","without","extract","input=","output=","crawl","depth=","pause="])
    except getopt.GetoptError:
      print('usage: torcrawl.py -h -v -w -u <fullPath> -o <outputFile>')
      sys.exit(2)
    for opt, arg in opts:
      
      # General
      if opt in ("-h", "--help"):
        print help
        sys.exit()
      elif opt in ("-v", "--verbose"):
        verbose = True
      elif opt in ("-u", "--url"):
        website = arg
      elif opt in ("-w", "--without"):
        withoutTor = True

      # Extract
      elif opt in ("-e", "--extract"):
        extractarg = True
      elif opt in ("-i", "--input"):
        inputFile = arg
      elif opt in ("-o", "--output"):
        outputFile = arg

      # Crawl
      elif opt in ("-c", "--crawl"):
        crawl = True
      elif opt in ("-d", "--cdepth"):
        cdepth = arg
      elif opt in ("-z", "--exclusions"):
        cexclus = arg
      elif opt in ("-s", "--simultaneous"):
        csimul = arg
      elif opt in ("-p", "--pause"):
        cpause = arg
      elif opt in ("-l", "--log"):
        logs = True
        

    if withoutTor == False:
      if verbose == True:
        checkTor()
      connectTor()

    if verbose == True:
      print('## URL: ' + website)
      checkIP()
    
    if crawl == True:
      # TODO: Set verbose variable in crawler
      lst = crawler(website, cdepth, cpause)
      lstfile = open('links.txt', 'w+')
      for item in lst:
        lstfile.write("%s\n" % item)
      lstfile.close()
      print("## File created on " + os.getcwd() + "/links.txt")
      if extractarg == True:
        inputFile = "links.txt"
        extractor(website, outputFile, inputFile)
    else: 
      # TODO: Set verbose variable in extractor
      extractor(website, outputFile, inputFile)
if __name__ == "__main__":
    main(sys.argv[1:])

