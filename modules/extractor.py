#!/usr/bin/python

import os
import sys
import urllib2

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
