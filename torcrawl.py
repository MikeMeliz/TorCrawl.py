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
import re
import getopt
import socket
import socks
import subprocess
from urllib2 import urlopen
from json import load
from collections import namedtuple

# TorCrawl Modules
from modules.crawler import *
from modules.extractor import *

# Check if TOR service is running
def checkTor():
    checkTor = subprocess.check_output(['ps', '-e'])
    def findWholeWord(w):
      return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
    if findWholeWord('tor')(checkTor):
      print("## TOR is ready!")
    else:
      print("## TOR is NOT running!")
      print('## Enable tor with \'service tor start\' or add -w argument')
      sys.exit(2)

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

# Check your IP from external website
def checkIP():
    try:
      webIPcheck = 'https://api.ipify.org/?format=json'
      my_ip = load(urlopen(webIPcheck))['ip']
      print '## Your IP: ' + my_ip
    except:
      e = sys.exc_info()[0]
      print( "Error: %s" % e + "\n## IP can't obtain \n## Is " + webIPcheck + "up?")
'''
# Write output to file
def extractorFile(outputFile, website):
    try:
      f = open(outputFile,'w')
      f.write(urllib2.urlopen(website).read())
      f.close()
      print '## File created on ' + os.getcwd() + '/' + outputFile
    except:
      e = sys.exc_info()[0]
      print("Error: %s" % e + "\n## Not valid URL \n## Did you forget \'http://\'?")

# Write output to terminal
def extractor(website):
    try:
      print urllib2.urlopen(website).read()
    except:
      e = sys.exc_info()[0]
      print("Error: %s" % e + "\n## Not valid URL \n## Did you forget \'http://\'?")
'''

def main(argv):
    verbose = False
    withoutTor = False
    outputToFile = False
    crawl = False
    cdepth = 1
    simultaneous = 1
    cpause = 0

    try:
      opts, args = getopt.getopt(argv,"hvcu:wo:d:p:",["help","verbose","url=","without","output=","crawl=","pause="])
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
      elif opt in ("-o", "--output"):
        outputFile = arg
        outputToFile = True

      # Extract
      elif opt in ("-e", "--extract"):
        extract = True
      elif opt in ("-i", "--input"):
        inputFile = arg
        inputFromFile = True

      # Crawl
      elif opt in ("-c", "--crawl"):
        crawl = True
      elif opt in ("-d", "--cdepth"):
        cdepth = arg
      elif opt in ("-e", "--exclusions"):
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
        lst = crawler(website, cdepth, cpause)
        lstfile = open('links.txt', 'w+')
        for item in lst:
          lstfile.write("%s\n" % item)
        lstfile.close()
        print("## File created on " + os.getcwd() + "/links.txt")
    else:
      if outputToFile == True:
        if verbose == True:
          print('## Filename: ' + outputFile)
        extractorFile(outputFile, website)
      else:
        extractor(website)


if __name__ == "__main__":
    main(sys.argv[1:])

