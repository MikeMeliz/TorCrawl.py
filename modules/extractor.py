#!/usr/bin/python

import os
import sys
import urllib2

# Write output to terminal
def extractor(website, outputFile, inputFile):
    if len(outputFile) > 0:
      try:
        f = open(outputFile,'w')
        f.write(urllib2.urlopen(website).read())
        f.close()
        print("## File created on " + os.getcwd() + "/" + outputFile)
      except:
        e = sys.exc_info()[0]
        print("Error: %s" % e + "\n## Not valid URL \n## Did you forget \'http://\'?")
    else:
      if len(inputFile) > 0:
        try:
          f = open(inputFile,'r')
          for line in f:
            print urllib2.urlopen(line).read()
        except:
          e = sys.exc_info()[0]
          print("Error: %s" % e + "\n## Not valid file")
      else:
        try:
          print urllib2.urlopen(website).read()
        except:
          e = sys.exc_info()[0]
          print("Error: %s" % e + "\n## Not valid URL \n## Did you forget \'http://\'?")
