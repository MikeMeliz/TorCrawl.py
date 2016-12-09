#!/usr/bin/python

help='''
Basic Information:
TorCrawl.py is a python -terminal based- script
to crawl and extract webpages through TOR network. 

Examples:
./torcrawl.py -u http://www.github.com 
./torcrawl.py -v -w -u http://www.github.com -o github.htm 
./torcrawl.py -u http://www.github.com | grep 'google-analytics'

General:
-h, --help        : Help
-v, --verbose     : Show steps
-u, --url         : URL of Webpage to crawl or extract
-w, --without     : Without the use of TOR Relay (default ON) 

Extract:
-e, --extract     : Extract page's code to terminal or file     (TODO)
-i, --input       : Input file with URLs                        (TODO)
-o, --output      : Output to file

Crawl:
-c, --
-d, --cdepth      : Set depth of crawl's travel (1-5)           (TODO)
-ce,--exclusions  : Paths that you don't want to include        (TODO)
-sp,--simultaneous: How many pages to visit at the same time    (TODO)
-p, --pause       : The length of time the crawler will pause   (TODO)
-l, --log         : A save log will let you see which URLs were (TODO)
                    visited and which were converted into data.
'''

import os
import sys
import re
import getopt
import socket
import urllib
import socks
import subprocess
from json import load
from urllib2 import urlopen

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

# Write output to file
def output(outputFile, website):
    try:
      f = open(outputFile,'w')
      f.write(urllib.urlopen(website).read())
      f.close()
      print '## File created on ' + os.getcwd() + '/' + outputFile
    except:
      e = sys.exc_info()[0]
      print("Error: %s" % e + "\n## Not valid URL \n## Did you forget \'http://\'?")

# Write output to terminal
def outputToTerm(website):
      try:
        print urllib.urlopen(website).read()
      except:
        e = sys.exc_info()[0]
        print("Error: %s" % e + "\n## Not valid URL \n## Did you forget \'http://\'?")
    
def main(argv):
    verbose = False
    outputToFile = False
    withoutTor = False

    try:
      opts, args = getopt.getopt(argv,"hvu:wo:",["help","verbose","url=","without","output="])
    except getopt.GetoptError:
      print('usage: torcrawl.py -h -v -w -u <fullPath> -o <outputFile>')
      sys.exit(2)
    for opt, arg in opts:
      if opt in ("-h", "--help"):
        print help
        sys.exit()
      elif opt in ("-v", "--verbose"):
        verbose = True
      elif opt in ("-u", "--url"):
        website = arg
      elif opt in ("-o", "--output"):
        outputFile = arg
        outputToFile = True
      elif opt in ("-w", "--without"):
        withoutTor = True
        
    if withoutTor == False:
      if verbose == True:
        checkTor()
      connectTor()

    if verbose == True:
      print('## URL: ' + website)
      checkIP()
    
    if outputToFile == True:
      if verbose == True:
        print('## Filename: ' + outputFile)
      output(outputFile, website)
    else:
      outputToTerm(website)
      
if __name__ == "__main__":
    main(sys.argv[1:])

'''
References & Credits:
Arguments: https://www.tutorialspoint.com/python/python_command_line_arguments.htm
Input/Output: https://docs.python.org/2/tutorial/inputoutput.html
Crawl through Tor: http://stackoverflow.com/questions/29784871/urllib2-using-tor-in-python (@Padraic Cunningham)
Public IP: http://stackoverflow.com/questions/9481419/how-can-i-get-the-public-ip-using-python2-7 (@Tadeck)
findWholeWord: http://stackoverflow.com/questions/20137032/trying-to-find-whole-words-not-just-partial-words-python/20137162 (@Goran)
'''