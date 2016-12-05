#!/usr/bin/python

__version__ = "0.1"
__all__ = ["TorCrawl"]
__author__ = "MikeMeliz"

help='''
Basic Information:
TorCrawl.py is a simple python -terminal based- script
to crawl webpage through TOR. 
It's created in that way that you can use grep to search
on the page.

Examples:
./TorCrawl.py -u http://www.github.com 
./TorCrawl.py -v -w -u http://www.github.com -o github.htm 
./TorCrawl.py -u http://www.github.com | grep 'google-analytics'

Arguments:
-h, --help     : Help
-v, --verbose  : Show steps
-u, --url      : URL of Webpage to crawl
-w, --without  : Without the use of TOR Relay (default ON) 
-o, --output   : Output to file
'''

import os
import sys
import getopt
import socket
import urllib
import socks
from json import load
from urllib2 import urlopen


def main(argv):
    my_ip = ''
    website = ''
    outputFile = ''
    verbose = False
    outputToFile = False
    withoutTor = False
    try:
       opts, args = getopt.getopt(argv,"hvu:wo:",["help","verbose","url=","without","output="])
    except getopt.GetoptError:
       print 'usage: torcrawl.py -h -v -w -u <fullPath> -o <outputFile>'
       sys.exit(2)
    for opt, arg in opts:
       if opt in ("-h", "--help"):
          print help
          sys.exit()
       elif opt in ("-v", "--verbose"):
          verbose = True
       elif opt in ("-u", "--url"):
          website = arg
          if verbose == True:
             print '## URL: ' + website
       elif opt in ("-o", "--output"):
          outputFile = arg
          outputToFile = True
          if verbose == True:
             print '## File: ' + outputFile
       elif opt in ("-w", "--without"):
          withoutTor = True
    if withoutTor == False:
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
         write_to_page( "<p>Error: %s</p>" % e )
    if verbose == True:
      my_ip = load(urlopen('https://api.ipify.org/?format=json'))['ip']
      print '## Your IP: ' + my_ip
    # Write webpage to file or output on terminal
    if outputToFile == True:
       try:
          f = open(outputFile,'w')
          f.write(urllib.urlopen(website).read())
          f.close()
       except:
          e = sys.exc_info()[0]
          write_to_page( "<p>Error: %s</p>" % e )
       print 'File created on ' + os.getcwd() + '/' + outputFile
    else:
        print urllib.urlopen(website).read()

if __name__ == "__main__":
    main(sys.argv[1:])

'''
References & Credits:
Arguments: https://www.tutorialspoint.com/python/python_command_line_arguments.htm
Input/Output: https://docs.python.org/2/tutorial/inputoutput.html
Crawl through Tor: http://stackoverflow.com/questions/29784871/urllib2-using-tor-in-python (@Padraic Cunningham)
Public IP: http://stackoverflow.com/questions/9481419/how-can-i-get-the-public-ip-using-python2-7 (@Tadeck)
'''