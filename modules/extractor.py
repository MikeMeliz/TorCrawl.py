#!/usr/bin/python

import os
import sys
import urllib.request, urllib.parse, urllib.error


# Input links from file and extract them into path/files
def cinex(inputFile, outpath):
	try:
		global f
		f = open(inputFile, 'r')
	# print f
	except IOError:
		e = sys.exc_info()[0]
		print(("Error: %s" % e + "\n## Can't open " + inputFile))

	for line in f:

		# Generate name for every file
		try:
			pagename = line.rsplit('/', 1)
			clpagename = str(pagename[1])
			clpagename = clpagename[:-1]
			if len(clpagename) == 0:
				outputFile = "index.htm"
			else:
				outputFile = clpagename
		except IndexError as e:
			print("Error: %s" % e)
			continue

		# Extract page to file
		try:
			f = open(outpath + "/" + outputFile, 'wb')
			f.write(urllib.request.urlopen(line).read())
			f.close()
			print(("## File created on " + os.getcwd() + "/" + outpath + "/" + outputFile))
		except:
			e = sys.exc_info()[0]
			print(("Error: %s" % e + "\n Can't write on file " + outputFile))


# Input links from file and extract them into terminal
def intermex(inputFile):
	try:
		f = open(inputFile, 'r')
		for line in f:
			print((urllib.request.urlopen(line).read()))
	except:
		e = sys.exc_info()[0]
		print(("Error: %s" % e + "\n## Not valid file"))


# Output webpage into a file
def outex(website, outputFile, outpath):
	# Extract page to file
	try:
		outputFile = outpath + "/" + outputFile
		f = open(outputFile, 'wb')
		f.write(urllib.request.urlopen(website).read())
		f.close()
		print(("## File created on " + os.getcwd() + "/" + outputFile))
	except:
		e = sys.exc_info()[0]
		print(("Error: %s" % e + "\n Can't write on file " + outputFile))


# Output to terminal
def termex(website):
	try:
		print((urllib.request.urlopen(website).read()))
	except (urllib.error.HTTPError, urllib.error.URLError) as e:
		print(("Error: (%s) %s" % (e, website)))
		return None


def extractor(website, crawl, outputFile, inputFile, outpath):
	# TODO: Return output to torcrawl.py
	if len(inputFile) > 0:
		if crawl:
			cinex(inputFile, outpath)
		# TODO: Extract from list into a folder
		# elif len(outputFile) > 0:
		# 	inoutex(website, inputFile, outputFile)
		else:
			intermex(inputFile)
	else:
		if len(outputFile) > 0:
			outex(website, outputFile, outpath)
		else:
			termex(website)
