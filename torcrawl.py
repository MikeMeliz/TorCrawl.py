#!/usr/bin/python

help='''

TorCrawl.py is a python script to crawl and extract (regular or onion) 
webpages through TOR network. 

usage: python torcrawl.py [options]
python torcrawl.py -u l0r3m1p5umD0lorS1t4m3t.onion 
python torcrawl.py -v -w -u http://www.github.com -o github.htm 
python torcrawl.py -v -u l0r3m1p5umD0lorS1t4m3t.onion -c -d 2 -p 5
python torcrawl.py -v -w -u http://www.github.com -c -d 2 -p 5 -e -o GitHub

General:
-h, --help         : Help
-v, --verbose      : Show more informations about the progress
-u, --url *.onion  : URL of Webpage to crawl or extract
-w, --without      : Without the use of Relay TOR 

Extract:
-e, --extract           : Extract page's code to terminal or file.
                          (Defualt: terminal)
-i, --input filename    : Input file with URL(s) (seperated by line)
-o, --output [filename] : Output page(s) to file(s) (for one page)

Crawl:
-c, --crawl       : Crawl website (Default output on /links.txt)
-d, --cdepth      : Set depth of crawl's travel (Default: 1)
-z, --exclusions  : Paths that you don't want to include (TODO)
-s, --simultaneous: How many pages to visit at the same time (TODO)
-p, --pause       : The length of time the crawler will pause 
                    (Default: 0)
-l, --log         : A save log will let you see which URLs were
                    visited (TODO)

GitHub: github.com/MikeMeliz/TorCrawl.py
License: GNU General Public License v3.0

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
    extractarg, verbose, withoutTor, outputToFile, crawl, logs = [False] * 6
    cdepth = simultaneous = 1
    cpause = 0
    website = outputFile = inputFile = outpath = ''

    try:
      opts, args = getopt.getopt(argv,'hvu:wei:o:cd:p:l',["help","verbose","url=","without","extract","input=","output=","crawl","depth=","pause=","log"])
    except getopt.GetoptError:
      print('usage: torcrawl.py [options]')
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
        
    # Connect to TOR
    if withoutTor == False:
      checkTor(verbose)
      connectTor()
    
    website = urlcanon(website, verbose)

    if verbose == True:
      checkIP()
      print('## URL: ' + website)

    # Create path for output
    if len(website) > 0:
      outpath = folder(website, verbose)
      if verbose == True:
        print("## Output Path: " + outpath)

    if crawl == True:
      lst = crawler(website, cdepth, cpause, outpath, logs, verbose)
      lstfile = open(outpath + '/links.txt', 'w+')
      for item in lst:
        lstfile.write("%s\n" % item)
      lstfile.close()
      print("## File created on " + os.getcwd() + "/" + outpath + "/links.txt")
      if extractarg == True:
        inputFile = outpath + "/links.txt"
        extractor(website, crawl, outputFile, inputFile, outpath, verbose)
    else: 
      extractor(website, crawl, outputFile, inputFile, outpath, verbose)
if __name__ == "__main__":
    main(sys.argv[1:])
