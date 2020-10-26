#!/usr/bin/python

import sys
import re
import subprocess
import os
from urllib.request import urlopen
from json import load
from urllib.parse import urlparse


def urlcanon(website, verbose):
	if not website.startswith("http"):
		if not website.startswith("www."):
			website = "www." + website
			if verbose:
				print(("## URL fixed: " + website))
		website = "http://" + website
		if verbose:
			print(("## URL fixed: " + website))
	return website


def extract_domain(url, remove_http=True):
	uri = urlparse(url)
	if remove_http:
		domain_name = f"{uri.netloc}"
	else:
		domain_name = f"{uri.netloc}://{uri.netloc}"
	return domain_name


# Create output path
def folder(website, verbose):
	outpath = website
	if not os.path.exists(outpath):
		os.makedirs(outpath)
	if verbose:
		print(("## Folder created: " + outpath))
	return outpath


# Check if TOR service is running
def checktor(verbose):
	checkfortor = subprocess.check_output(['ps', '-e'])

	def findwholeword(w):
		return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

	if findwholeword('tor')(str(checkfortor)):
		if verbose:
			print("## TOR is ready!")
	else:
		print("## TOR is NOT running!")
		print('## Enable tor with \'service tor start\' or add -w argument')
		sys.exit(2)


# Check your IP from external website
def checkip():
	try:
		webipcheck = 'https://api.ipify.org/?format=json'
		my_ip = load(urlopen(webipcheck))['ip']
		print(('## Your IP: ' + my_ip))
	except:
		e = sys.exc_info()[0]
		print(("Error: %s" % e + "\n## IP can't obtain \n## Is " + webipcheck + "up?"))
