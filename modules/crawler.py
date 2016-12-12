#!/usr/bin/python

import re
import urllib2
import time
from BeautifulSoup import BeautifulSoup

# Core of crawler
def crawler(website, cdepth, cpause):
    lst = set()
    ordlst = list()
    ordlst.insert(0, website)
    ordlstind = 0
    urlpath = website
    idx = 0
    
    print("## Crawler Started from " + website + " with step " + str(cdepth) + " and wait " + str(cpause))
    
    # Depth
    for x in range(0, int(cdepth)):
      
      # For every element of list
      for item in ordlst: 

        # Check if is the first element
        if ordlstind > 0:
          try:
            html_page = urllib2.urlopen(item)
          except urllib2.HTTPError, e:
            print e
        else:
          html_page = urllib2.urlopen(website)
        
        soup = BeautifulSoup(html_page)
        for link in soup.findAll('a'):        
          link = link.get('href')
          
          # Excludes
          
          # None (to avoid NoneType exceptions)
          if link == None:
            continue
          # #links
          elif link.startswith('#'):
            continue
          # External links
          elif link.startswith('http') and not link.startswith(website):
            continue
      
          # Canonicalization
          
          # Already formated
          if link.startswith(website):
            lst.add(link)
          # For relative paths with / infront
          elif link.startswith('/'):
            if website[-1] == '/':
              finalLink = website[:-1] + link
            else:
              finalLink = website + link
            lst.add(finalLink)
          # For relative paths without /
          elif re.search('^.*\.(html|htm|aspx|php|doc|css|js|less)$', link, re.IGNORECASE):
            # Pass to 
            if website[-1] == '/':
              finalLink = website + link
            else:
              finalLink = website + "/" + link
            lst.add(finalLink)

        ordlstind = ordlstind + 1
        # Pass new on list and re-set it to delete duplicates
        ordlst = ordlst + list(set(lst))
        ordlst = list(set(ordlst))
        #print("\x08## List's size: " + str(len(ordlst)))
        # Pause time
        if (ordlst.index(item) != len(ordlst)-1) and cpause > 0:
          #print("## Waiting: " + str(cpause) + "sec")
          time.sleep(float(cpause))

      print("## Step " + str(x+1) + " completed with: " + str(len(ordlst)) + " results")

    # TODO: Order the list 

    return ordlst