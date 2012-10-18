#!/usr/bin/env python
# -*- coding: cp1252 -*-
# Contact: Simon Judge <simon.judge@nhs.net> 
# Date: Nov 2012

#
#	Inflict Template 
#		This program takes a Grid 2 page (file) with some content in it.  It then 'inflicts' this template on a other grids (as chosen).
#		USE WITH EXTREME CAUTION!!! This will obliterate all the content in the locations of template cells.  
# 		Only cells that are blank will not be copied from the template - to do this, in the grid, choose 'Clear this cell' and/or choose the style "Blank cell (no style)".
#		This _INCLUDES_ cells hidden behind other cells that are stretched.


#		The intention of this program is to allow application of a consistent template(s) across an entire grid (for example, home, back, copy etc)
#
#	1.  Copy in the template file
#	2.	Find grids in the white list and not in the blacklist
#	2. 	Overwrite grid.xml files with template.

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


def parsexml(xml='grid.xml'):
	
	parser = etree.XMLParser(strip_cdata=False)
	tree = etree.parse(xml, parser)                 # Parse the template file
	return tree

def parse_grids(gridxml='grid.xml',outputpath='.',userdir='.', templatetree=[],
				excludehidden=False, ignoregrids=[],):
	

 	if (outputpath == '.'):
		outinplace = True
	else:
		outputpath = outputpath + '/'
		outinplace=False 

	# Work out which cells need inflicting.
	
	template_cells = templatetree.xpath(".//cell")
	template_xys = []
	for cell in template_cells:
		style = ''.join(cell.xpath(".//stylepreset/text()"))
		if style != "Blank cell (no style)":
			template_xys.append([cell.get("x"), cell.get("y")])
	
	for r,d,f in os.walk(userdir):                                  # Parse any directory, only picking up on grid.xml files.
		page = os.path.split(r)[1]
		if page not in ignoregrids:
			for files in f:

				if files.endswith("grid.xml"):
#### ******** ITTERATE OVER ALL GRID FILES. ********** ########
					pth = os.path.join(r,files)
					
					if (outinplace):                                # Check to see if output directory specified, if not output to the Grid directories.
						outputpath = r + '/'

					tree = parsexml(pth)                 # Parse the file
					cells = tree.xpath(".//cell")
					cellscopy=cells

					print len(cells)
					for cell in cellscopy:
#### ******* Itterate over all cells in a grid ********** #########
						print [cell.get("x"), cell.get("y")] 
						x=cell.get("x")
						y=cell.get("y")
						if [x,y] in template_xys:
							#cell.clear()
							xpathstring=(".//*[@x={0}][@y={1}]").format(x, y)
							template_cell=templatetree.xpath(xpathstring)
							cell=template_cell 

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
	-t, --template		- path to the template xml file.

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
	templatetree=[]
	excludehidden=False
	ignoregrids=[]



	try:
		opts, args = getopt.getopt(sys.argv[1:], "houcgbxwsdv", ["help", "output=", "userdir=","ignoregrids=", "template="])
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
		elif o in ("-t", "--template"):
			if os.path.exists(os.path.normpath(a)):                
				templatetree = parsexml(os.path.normpath(a))
			else:
				assert False, "non-existent template file: " + os.path.normpath(a) 
		else:
			assert False, "unhandled option"
	
	parse_grids(gridxml,outputpath,userdir,templatetree, excludehidden, ignoregrids)

if __name__ == "__main__":
	main()