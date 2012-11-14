#!/usr/bin/env python
# -*- coding: cp1252 -*-
# Contact: Simon Judge <simon.judge@nhs.net>
# Date: Nov 2012

#
#	Purge
# 	Purge un-used grids and/or styles
# 	USE WITH EXTREME CAUTION. THIS DELETES THINGS!!!

# -*- coding: iso-8859-15 -*-

# Utils
import sys
sys.path.append('../utils')


import pdb
import os.path, errno, re
from lxml import etree
import getopt, sys, csv
from unicodecsv import UnicodeWriter  
import shutil

def make_dirs(path):
	if not os.path.exists(path):
		os.makedirs(path)
	return path

def filetolist(file):
	text_file = open(file, "r")
	s = text_file.read()
	l = re.split('\n',s)
	l=filter(None, l) 
	return l

def parse_grids(gridxml='grid.xml',outputpath='.',userdir='.',
				ignoregrids=[], blackliststyles=[], purgestyles=False, purgegrids=False ):
	
	stylelist = []
	gridlist = []
	gridcount = 0
	
 	if (outputpath == '.'):
		outinplace = True
	else:
		outputpath = outputpath + '/'
		outinplace=False 
	
	for r,d,f in os.walk(userdir):                                  # Parse any directory (only picking up on grid.xml files) to list grids and styles. 
		page = os.path.split(r)[1]
		if page not in ignoregrids:
			for files in f:

				if files.endswith("grid.xml"):
#### ******** ITTERATE OVER ALL GRID FILES. ********** ########
					gridcount = gridcount+1
					pth = os.path.join(r,files)
					
					if (outinplace):                                # Check to see if output directory specified, if not output to the Grid directories.
						outputpath = r + '/'
					parser = etree.XMLParser(strip_cdata=False)
					tree = etree.parse(pth, parser)                 # Parse the file
					cells = tree.xpath(".//cell")						

					for cell in cells:
#### ******* Itterate over all cells in a grid ********** #########
						style = ''.join(cell.xpath(".//stylepreset/text()"))
						command_id = cell.xpath(".//id/text()") 

						if style not in blackliststyles:
# Implement white list too?
							if style not in stylelist:		# check if exists in list already
								stylelist.append(style)		# if not, add it.
						
							if ("jump.to" in command_id):    # We are only interested if in jump cells
								cellchildren = cell.getchildren()
								for cellchild in cellchildren:
									commands = cellchild.getchildren()
									for command in commands:
										id = command.find("id")
										if id is not None:
											if id.text == "jump.to":
												parameters = command.findall("parameter")
												for parameter in parameters:
													if "1" in parameter.xpath(".//@index"): 
														jumpto = parameter.text.strip()
														if jumpto not in gridlist:
															gridlist.append(jumpto)
															
	print gridlist
	print stylelist
	print "Number of linked grids:"
	print len(gridlist)
	print "Total Number of grids"
	print gridcount
	print "Number of used styles:"
	print len(stylelist)

	if purgegrids:
		gridfolder = 0
		for r,d,f in os.walk(userdir):                                  # Parse any directory (only picking up on grid.xml files) to DELETE grids and styles. 
			grid = os.path.split(r)[1]
			if grid not in ignoregrids:
				if grid not in gridlist:
					if (os.path.split(os.path.split(r)[0])[1]) == "Grids" and (grid != ''):
			################## EXTRA PRECAUTIONS... GRIDS ONLY... not remove /grids directory!!!
						#pdb.set_trace()	
						shutil.rmtree(r)
						
						########## DOESN'T REMOVE IT FROM THE GRIDNAMES.txt file....  
	

						
def usage():
	print """
	This program takes a Grid 2 User folder looks at which grids link where and REMOVES ALL GRIDS THAT ARE NOT LINKED TO.
	It also looks at what styles are not used and REMOVES THESE FROM THE STYLES LIST. 
	The intention of this program is to purge messy grid sets after design is complete.
	
	Note text files must have a 'new line' at the end of all lines - including the last, in order to be properly read in.
	
	Flags:
	-h, --help          - This screen
	-v                  - Verbose (debug)
	-o, --output        - File path of where you would like the csv/wordlist files. 
							Set to SAME to be same directory of grid.xml files (default)
	-u, --userdir=       - File path of the user Folder you want to analyse
	-i, --ignoregrids=   - Exclude grids listed from a text file (e.g, home, dogs)
	-b, --blackliststyles    - Exclude styles listed from a text file (e.g. colours, jumpcells)
	-s					- purge styles
	-g					- purge grids

	Example Usage:
	purge.py --userdir="C:\Documents and Settings\All Users\Documents\SensorySoftware\The Grid 2\Users\USERNAME" --ignorecells="ignorecells.txt" --ignoregrids="ignoregrids.txt" --blackliststyles="ignorestyles.txt" --stylemapping="stylemapping.txt"
	
	Requirements:
	Python 2.3, Lxml, unicodecsv
	
	Author:
	Simon Judge [simon {dot}judge{a t}nhs.net, fragrantly based on brilliant code by Will Wade[will@e-wade.net]
	"""              
					
def main():
	gridxml='grid.xml'
	outputpath ='.'
	userdir='.'
	ignoregrids=[]
	blackliststyles=[]
	purgestyles = False
	purgegrids = False

	try:
		opts, args = getopt.getopt(sys.argv[1:], "houibsg", ["help", "output=", "userdir=","ignoregrids=", "blackliststyles="])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	output = None
	verbose = False
	for o, a in opts:
		if o == "-v":
			verbose = True
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-o", "--output"):
			if os.path.exists(os.path.normpath(a) + '/'):
				outputpath = os.path.normpath(a) + '/'
			else:
				assert False, "non-existent output directory: " + os.path.normpath(a) + '/'
		elif o in ("-u", "--userdir"):
			if os.path.exists(os.path.normpath(a) + '/'):
				userdir = os.path.normpath(a) + '/'
			else:
				assert False, "non-existent user directory: " + os.path.normpath(a) + '/'
		elif o in ("-x", "--excludehidden"):
			excludehidden = True       
		elif o in ("-i", "--ignoregrids"):
			if os.path.exists(os.path.normpath(a)):                
				ignoregrids = filetolist(os.path.normpath(a))
			else:
				assert False, "non-existent ignoregrids file: " + os.path.normpath(a) 
		elif o in ("-b", "--blackliststyles"):
			if os.path.exists(os.path.normpath(a)):                
				blackliststyles = filetolist(os.path.normpath(a))
			else:
				assert False, "non-existent blacklist styles file: " + os.path.normpath(a) 
		elif o in ("-s"):
			purgestyles = True
		elif o in ("-g"):
			purgegrids = True
		else:
			assert False, "unhandled option"
	
	parse_grids(gridxml,outputpath,userdir,ignoregrids, blackliststyles, purgestyles, purgegrids)

if __name__ == "__main__":
	main()