#!/usr/bin/python

import os
import sys
import urllib2

# Input links from file and extract them into path/files
def cinex(website, inputFile, outpath):
    try:
      f = open(inputFile,'r')
      #print f
    except:
      e = sys.exc_info()[0]
      print("Error: %s" % e + "\n## Can't open " + inputFile)
    
    for line in f:  
      
      # Generate name for every file 
      pagename = line.rsplit('/', 1)
      clpagename = str(pagename[1])
      clpagename = clpagename[:-1]
      if len(clpagename) == 0:
        outputFile = "index.htm"
      else:
        outputFile = clpagename

      # Extract page to file
      try:
        f = open(outpath + "/" + outputFile,'w')
        f.write(urllib2.urlopen(line).read())
        f.close()
        print("## File created on " + os.getcwd() + "/" + outpath + "/" + outputFile)
      except:
        e = sys.exc_info()[0]
        print("Error: %s" % e + "\n Can't write on file " + outputFile)

# Input links from file and extract them into terminal
def intermex(inputFile):
    try:
      f = open(inputFile,'r')
      for line in f:
        print urllib2.urlopen(line).read()
    except:
      e = sys.exc_info()[0]
      print("Error: %s" % e + "\n## Not valid file")

# Output webpage into a file
def outex(website, outputFile, outpath):
    # Extract page to file
    try:
      outputFile = outpath + "/" + outputFile
      f = open(outputFile,'w')
      f.write(urllib2.urlopen(website).read())
      f.close()
      print("## File created on " + os.getcwd() + "/" + outputFile)
    except:
      e = sys.exc_info()[0]
      print("Error: %s" % e + "\n Can't write on file " + outputFile)

# Ouput webpage into terminal
def termex(website):
    try:
      print urllib2.urlopen(website).read()
    except:
      e = sys.exc_info()[0]
      print("Error: %s" % e + "\n## Not valid URL \n## Did you forget \'http://\'?")


def extractor(website, crawl, outputFile, inputFile, outpath, verbose):
    if len(inputFile) > 0:
      if crawl == True:
        cinex(website, inputFile, outpath)
      # TODO: Extract from list into a folder
      #elif len(outputFile) > 0:
      # inoutex(website, inputFile, outputFile)
      else:
        intermex(inputFile)
    else:
      if len(outputFile) > 0:
        outex(website, outputFile, outpath)
      else:
        termex(website)

    # TODO: Return output to torcrawl.py