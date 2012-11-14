#!/usr/bin/env python
# -*- coding: cp1252 -*-
# Contact: Simon Judge <simon.judge@nhs.net>
# Date: Nov 2012

#
#	Styles to ScanBlock	
#		This program takes a Grid 2 User folder and changes the scan blocks of cells based on their style. 
#		The intention of this program is to allow application of a consistent scan pattern across an entire grid set, based on the type of cell.
#
#	1.  Determine the scanblock of a cell based on its style.
#	2. 	Overwrite grid.xml files 

# -*- coding: iso-8859-15 -*-

# Utils
import sys
sys.path.append('../utils')


import pdb
import os.path, errno, re
from lxml import etree
import getopt, sys, csv
from unicodecsv import UnicodeWriter  


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
				excludehidden=False,
				ignoregrids=[],ignorecells=[], blackliststyles=[], stylemapping=[], blockscan=[]):
	
	# Create list of styles that are being enforced and index
	stylelist = []
	styleindex = []
	blocklist = []
	blockindex = []
	
	for style in stylemapping:
		
		stylesplit = re.split('\s+', style, maxsplit=1)
		styleindex.append(stylesplit[0])
		stylelist.append(stylesplit[1])
	print stylelist
			
	for block in blockscan:
		blocksplit = re.split('\s+', block, maxsplit=1)
		blockindex.append(blocksplit[0])
		blocklist.append(blocksplit[1])
		

 	if (outputpath == '.'):
		outinplace = True
	else:
		outputpath = outputpath + '/'
		outinplace=False 
	
	for r,d,f in os.walk(userdir):                                  # Parse any directory, only picking up on grid.xml files.
		page = os.path.split(r)[1]
		if page not in ignoregrids:
			for files in f:

				if files.endswith("grid.xml"):
#### ******** ITTERATE OVER ALL GRID FILES. ********** ########
					pth = os.path.join(r,files)
					
					if (outinplace):                                # Check to see if output directory specified, if not output to the Grid directories.
						outputpath = r + '/'
					parser = etree.XMLParser(strip_cdata=False)
					tree = etree.parse(pth, parser)                 # Parse the file
					cells = tree.xpath(".//cell")						

					for cell in cells:
#### ******* Itterate over all cells in a grid ********** #########
						tt = ''.join(cell.xpath("(.//caption)/text()"))
						style = ''.join(cell.xpath(".//stylepreset/text()"))

						if style not in blackliststyles:
# Implement white list too?
							if  tt not in ignorecells:
						
								if style in stylelist:									
									scanblock =cell.find('scanblock')
									scanblock.text = str(2**int(styleindex[stylelist.index(style)]))
								else:
									scanblock =cell.find('scanblock')
									scanblock.text = '0'

					auditory = tree.find(".//auditory")
					#pdb.set_trace()
					if auditory:
						auditory.clear()
					else:
						#pdb.set_trace()
						root=tree.getroot()
						auditory=etree.SubElement(root, 'auditory')
					for block in blocklist:
						cue=etree.SubElement(auditory,'cue')
						cue.set('id', "blk"+blockindex[blocklist.index(block)])
						cue.text= str(block)
					print etree.dump(auditory)
					
										
					file_out = open( outputpath + 'grid.xml', 'wb')
					file_out.write('<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(tree, pretty_print=True, encoding='utf-8'))
					file_out.close()
							  

						
def usage():
	print """
	This program takes a Grid 2 User folder and changes the scan blocks of cells based on their style. 
	The intention of this program is to allow application of a consistent scan pattern across an entire grid set, based on the type of cell.
	
	Note text files must have a 'new line' at the end of all lines - including the last, in order to be properly read in.
	
	Flags:
	-h, --help          - This screen
	-v                  - Verbose (debug)
	-o, --output        - File path of where you would like the csv/wordlist files. 
							Set to SAME to be same directory of grid.xml files (default)
	-u, --userdir=       - File path of the user Folder you want to analyse
	-c, --ignorecells=   - Exclude cells listed from a text file (e.g, back, jump)
	-g, --ignoregrids=   - Exclude grids listed from a text file (e.g, home, dogs)
	-b, --blackliststyles    - Exclude styles listed from a text file (e.g. colours, jumpcells)
	-x, --excludehidden - Exclude hidden cells from the analysis
	-s, --stylemapping	- File mapping styles to scan block. First line is scan block 0, second, block 1 etc.
	-l, --blockscan

	Example Usage:
	StylesToScanBlock.py --userdir="C:\Documents and Settings\All Users\Documents\SensorySoftware\The Grid 2\Users\USERNAME" --ignorecells="ignorecells.txt" --ignoregrids="ignoregrids.txt" --blackliststyles="ignorestyles.txt" --stylemapping="stylemapping.txt"
	
	Requirements:
	Python 2.3, Lxml, unicodecsv
	
	Author:
	Simon Judge [simon {dot}judge{a t}nhs.net, fragrantly based on brilliant code by Will Wade[will@e-wade.net]
	"""              
					
def main():
	gridxml='grid.xml'
	outputpath ='.'
	userdir='.'
	excludehidden=False
	ignoregrids=[]
	ignorecells=[]
	blackliststyles=[]
	stylemapping=[]
	blockscan=[]


	try:
		opts, args = getopt.getopt(sys.argv[1:], "houcgbxwsl", ["help", "output=", "userdir=","ignorecells=","ignoregrids=", "blackliststyles=", "stylemapping=", "blockscan="])
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
		elif o in ("-g", "--ignoregrids"):
			if os.path.exists(os.path.normpath(a)):                
				ignoregrids = filetolist(os.path.normpath(a))
			else:
				assert False, "non-existent ignoregrids file: " + os.path.normpath(a) 
		elif o in ("-c", "--ignorecells"):
			if os.path.exists(os.path.normpath(a)):
				ignorecells = filetolist(os.path.normpath(a))
			else:
				assert False, "non-existent ignorecells file: " + os.path.normpath(a)
		elif o in ("-b", "--blackliststyles"):
			if os.path.exists(os.path.normpath(a)):                
				blackliststyles = filetolist(os.path.normpath(a))
			else:
				assert False, "non-existent blacklist styles file: " + os.path.normpath(a) 
		elif o in ("-s", "--stylemapping"):
			if os.path.exists(os.path.normpath(a)):                
				stylemapping = filetolist(os.path.normpath(a))
			else:
				assert False, "non-existent blacklist styles file: " + os.path.normpath(a) 
		elif o in ("-l", "--blockscan"):
			if os.path.exists(os.path.normpath(a)):                
				blockscan = filetolist(os.path.normpath(a))
			else:
				assert False, "non-existent blockscan styles file: " + os.path.normpath(a) 
		else:
			assert False, "unhandled option"
	
	parse_grids(gridxml,outputpath,userdir,excludehidden, ignoregrids, ignorecells, blackliststyles, stylemapping, blockscan)

if __name__ == "__main__":
	main()