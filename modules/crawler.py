#!/usr/bin/python

import os
import sys
import re
import urllib2
import time
from BeautifulSoup import BeautifulSoup

# Exclude links that we dont need
def excludes(link, website, outpath):
    # BUG: For NoneType Exceptions, got to find a solution here
    if link == None:
      return True
    # #links
    elif '#' in link:
      return True
    # External links
    elif link.startswith('http') and not link.startswith(website):
      lstfile = open(outpath + '/extlinks.txt', 'w+')
      lstfile.write(link.encode('utf-8') + "\n")
      lstfile.close()
      return True
    # Telephone Number
    elif link.startswith('tel:'):
      lstfile = open(outpath + '/telephones.txt', 'w+')
      lstfile.write(link.encode('utf-8') + "\n")
      lstfile.close()
      return True
    # Mails
    elif link.startswith('mailto:'):
      lstfile = open(outpath + '/mails.txt', 'w+')
      lstfile.write(link.encode('utf-8') + "\n")
      lstfile.close()
      return True
    # Type of files
    elif re.search('^.*\.(pdf|jpg|jpeg|png|gif|doc)$', link, re.IGNORECASE):
      return True

# Canonicalization of the link
def canonical(link, website):
    # Already formated
    if link.startswith(website):
      return link
    # For relative paths with / infront
    elif link.startswith('/'):
      if website[-1] == '/':
        finalLink = website[:-1] + link
      else:
        finalLink = website + link
      return finalLink
    # For relative paths without /
    elif re.search('^.*\.(html|htm|aspx|php|doc|css|js|less)$', link, re.IGNORECASE):
      # Pass to 
      if website[-1] == '/':
        finalLink = website + link
      else:
        finalLink = website + "/" + link
      return finalLink   
    # Clean links from '?page=' arguments       


# Core of crawler
def crawler(website, cdepth, cpause, outpath, logs, verbose):
    lst = set()
    ordlst = []
    ordlst.insert(0, website)
    ordlstind = 0
    idx = 0
    
    if logs == True:
      logfile = open(outpath + '/log.txt', 'w+')
    
    print("## Crawler Started from " + website + " with step " + str(cdepth) + " and wait " + str(cpause))
    
    # Depth
    for x in range(0, int(cdepth)):
      
      # For every element of list
      for item in ordlst: 

        # Check if is the first element
        if ordlstind > 0:
          try:
            if item != None:
              html_page = urllib2.urlopen(item)
          except urllib2.HTTPError, e:
            print e
        else:
          html_page = urllib2.urlopen(website)
          ordlstind += 1

        soup = BeautifulSoup(html_page)
        
        # For each <a href=""> tag
        for link in soup.findAll('a'):        
          link = link.get('href')
          
          if excludes(link, website, outpath):
            continue
          
          verlink = canonical(link, website)
          lst.add(verlink)
        
        # TODO: For each <img src="">
        # for img in soup.findAll('img')
        #   img = link.get('src')
        #   if imgexludes(link, website)
        #     continue
        #
        #   verlink = imgcanonical(link, website)
        #   lst.add(verlink)

        # TODO: For each <script src="">
        # for link in soup.findAll('script'):        
        #   link = link.get('src')
        #   
        #   if screxcludes(link, website):
        #     continue
        #   
        #   verlink = scrcanonical(link, website)
        #   lst.add(verlink)

        # Pass new on list and re-set it to delete duplicates
        ordlst = ordlst + list(set(lst))
        ordlst = list(set(ordlst))
        
        if verbose == True:
          sys.stdout.write("-- Results: " + str(len(ordlst)) + "\r")
          sys.stdout.flush()

        # Pause time
        if (ordlst.index(item) != len(ordlst)-1) and cpause > 0:
          time.sleep(float(cpause))

        # Keeps logs for every webpage visited
        if logs == True:
          logfile.write("%s\n" % item)

      print("## Step " + str(x+1) + " completed with: " + str(len(ordlst)) + " results")

    if logs == True:
      logfile.close()

    ordlst.sort()
    return ordlst