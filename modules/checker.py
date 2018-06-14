#!/usr/bin/python

import sys
import re
import subprocess
import os
from urllib2 import urlopen
from json import load

# Canonicalization of URL
def urlcanon(website, verbose):
    if not website.startswith("http"):
      if not website.startswith("www."):
        website = "www." + website
        if verbose == True:
          print("## URL fixed: " + website)
      website = "http://" + website
      if verbose == True:
        print("## URL fixed: " + website)
    return website

#Create output path
def folder(website, verbose):
    if website.startswith('http'):
      outpath = website.replace("http://","")
    if website.startswith('https'):
      outpath = website.replace("https://","")
    else:
      outpath = website
    if outpath.endswith('/'):
      outpath = outpath[:-1]
    if not os.path.exists(outpath):
      os.makedirs(outpath)
    if verbose == True:
      print("## Folder created: " + outpath)
    return outpath

# Check if TOR service is running
def checkTor(verbose):
    checkTor = subprocess.check_output(['ps', '-e'])
    def findWholeWord(w):
      return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
    if findWholeWord('tor')(checkTor):
      if verbose == True:
        print("## TOR is ready!")
    else:
      print("## TOR is NOT running!")
      print('## Enable tor with \'service tor start\' or add -w argument')
      sys.exit(2)

# Check your IP from external website
def checkIP():
    try:
      webIPcheck = 'https://api.ipify.org/?format=json'
      my_ip = load(urlopen(webIPcheck))['ip']
      print '## Your IP: ' + my_ip
    except:
      e = sys.exc_info()[0]
      print( "Error: %s" % e + "\n## IP can't obtain \n## Is " + webIPcheck + "up?")
