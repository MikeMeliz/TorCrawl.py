#!/usr/bin/python

import os
import sys
import urllib2

# TODO: Split extractor into functions
def extractor(website, outputFile, inputFile):
    # Input links from file
    if len(inputFile) > 0:
      
      if len(outputFile) > 0:
        # BUG: Names end with ?
        # Read link file and create new path
        try:
          f = open(inputFile,'r')
          newpath = outputFile
          if not os.path.exists(newpath):
            os.makedirs(newpath)
        except:
          e = sys.exc_info()[0]
          print("Error: %s" % e + "\n## Can't open " + inputFile)
        
        for line in f:  
          # Generate name for every file 
          pagename = line.rsplit('/', 1)
          if len(pagename[1]) == 0:
            pagename[1] = index.htm
          else:
            outputFile = str(pagename[1])
          # Extract page to file
          try:
            f = open(newpath + "/" + outputFile,'w')
            f.write(urllib2.urlopen(website).read())
            f.close()
            print("## File created on " + os.getcwd() + "/" + outputFile)
          except:
            e = sys.exc_info()[0]
            print("Error: %s" % e + "\n Can't write on file " + outputFile)
      else:     
        try:
          f = open(inputFile,'r')
          for line in f:
            print urllib2.urlopen(line).read()
        except:
          e = sys.exc_info()[0]
          print("Error: %s" % e + "\n## Not valid file")
    # Juct extract the website to terminal
    else:
      try:
        print urllib2.urlopen(website).read()
      except:
        e = sys.exc_info()[0]
        print("Error: %s" % e + "\n## Not valid URL \n## Did you forget \'http://\'?")
