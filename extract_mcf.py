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



