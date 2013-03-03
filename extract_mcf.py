#!/usr/bin/python

# Copyright (c) 2013, Heiko Reese <desura@heiko-reese.de>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.  Redistributions in binary
# form must reproduce the above copyright notice, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided with
# the distribution.  Neither the name of the "no org" nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.  THIS SOFTWARE IS PROVIDED
# BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import xml.etree.cElementTree as et
from pprint import pprint
import os
import bz2
import hashlib
import tempfile
import urllib2

# create temporary directory
destdir = tempfile.mkdtemp(dir='.')

# retrieve update description
print "Retrieving desura update description from http://www.desura.com/api/appupdate"
response = urllib2.urlopen('http://www.desura.com/api/appupdate')
appupdate = response.read()

# parse xml
tree = et.fromstring(appupdate)
files = tree.findall('.//{http://www.desura.com/XMLSchema}file')

# read archive
#with open('1528.mcf', 'r') as fh:
#	mcf = bytearray(fh.read())

# retrieve update
mcf_url = tree.find('{http://www.desura.com/XMLSchema}mcf').find('{http://www.desura.com/XMLSchema}url').text
print "Retrieving desura update archive from %s (this might take a while)" % (mcf_url)
response = urllib2.urlopen(mcf_url)
mcf = response.read()

# loop over all files
for f in files:
	# extract attrs
	name     = f.findall('{http://www.desura.com/XMLSchema}name')[0].text
	path     = f.findall('{http://www.desura.com/XMLSchema}path')[0].text
	offset   = f.findall('{http://www.desura.com/XMLSchema}offset')[0].text
	size     = f.findall('{http://www.desura.com/XMLSchema}size')[0].text
	csize    = f.findall('{http://www.desura.com/XMLSchema}csize')[0].text
	nom_csum = f.findall('{http://www.desura.com/XMLSchema}nom_csum')[0].text
	com_csum = f.findall('{http://www.desura.com/XMLSchema}com_csum')[0].text
	
	# fix windows pathsep
	path = path.replace('\\', '/')
	# remove leading slash
	if path.startswith('/'):
		path = path[1:]
	localpath = os.path.join(destdir, path)
	# create path
	try:
		os.makedirs(localpath)
	except OSError:
		pass
	
	filename = os.path.join(localpath, name)
	
	# extract compressed image
	img = mcf[int(offset):int(offset)+int(csize)]
	
	if hashlib.md5(img).hexdigest() != com_csum:
		print "Compressed checksum does not match."
		next
	
	# decompress image
	uncompressed_img = bz2.decompress(img)
	
	if hashlib.md5(uncompressed_img).hexdigest() != nom_csum:
		print "Compressed checksum does not match."
		next
	
	# write file
	print "Writing %d bytes to file %s" % (int(size), filename)
	with open(filename, 'wb') as fh:
		fh.write(uncompressed_img)



