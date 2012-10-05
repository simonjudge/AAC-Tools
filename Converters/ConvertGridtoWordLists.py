#!/usr/bin/env python
# -*- coding: cp1252 -*-
# Contact: Will Wade <will@e-wade.net>
# Date: Jan 2012

# -*- coding: iso-8859-15 -*-

# Utils
import sys
sys.path.append('../utils')


""" Grid to Wordlist.
- Export Grids as CSV files for analysis. Seperate files or One file. set location of where
- Export grids as wordlist files - pass flag to rewrite all the grids as wordlist Grids
 (NB Pass the -excludecommon and -excludewords to exclude common and your own wordlists to convert. Useful for template pages)
 
 TODO:
 
 Tidy up wordlists - add CDATA to existing wordlists and new-lines to generated wordlists.
"""
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
				excludehidden=False,outputwordlists=True,
				ignoregrids=[],ignorecells=[], blackliststyles=[],singlefile=False, outputcsv=False, word_length=2, merge_lists=False):
# gridxml,outputpath,userdir,excludehidden,outputwordlists, ignoregrids, ignorecells, singlefile, outputcsv
	'''
	Parse Grid.xml files recursively. Extract Vocabulary and store it out as CSV files and/or as Wordlist files
	'''

	# Get gridsetname
	for r,d,f in os.walk(userdir):                                  # Parse  directories to find Grids directory
		#pdb.set_trace()
		if "Grids" in d:
			gridsetname=os.path.split(os.path.normpath(r))[1]

	# outputing to Grid folders or other output folder?
	# Check to see if output directory specified, if not output to the Grid directories.
	if (outputpath == '.'):
		outinplace = True
	else:
		outputpath = outputpath + '/'
		outinplace=False 

	# outputing to single file?
	if(singlefile):
		if(outputwordlists):
			file_out = open(outputpath +  gridsetname +'.xml', 'wb')
			wordlist = etree.Element("wordlist")
		if(outputcsv):
			vocabWriter = UnicodeWriter(open(outputpath + 'vocab.csv', 'wb'), delimiter=',', quotechar='"')
	
	for r,d,f in os.walk(userdir):                                  # Parse any directory, only picking up on grid.xml files.
		page = os.path.split(r)[1]
		if page not in ignoregrids:
			for files in f:

				if files.endswith("grid.xml"):
#### ******** ITTERATE OVER ALL GRID FILES. ********** ########
					pth = os.path.join(r,files)
					existing_wordlist = False
					
					if (outinplace):                                # Check to see if output directory specified, if not output to the Grid directories.
						outputpath = r + '/'
					parser = etree.XMLParser(strip_cdata=False)
					tree = etree.parse(pth, parser)                 # Parse the file
					if(tree.xpath(".//licencekey") == []):          # does it have a licencekey? Bugger if it has 
						readpictures = True
					else:
						readpictures = False                        # So this grid is licenced. Dont try and read the pictures
					cells = tree.xpath(".//cell")
						
					if(singlefile == False):
						if(outputwordlists):
							wordlist = etree.Element("wordlist")
						if (outputcsv):
							vocabWriter = UnicodeWriter(open(outputpath + page + '.csv', 'wb'), delimiter=',', quotechar='"')


					for cell in cells:
#### ******* Itterate over all cells in a grid ********** #########
						autocells = cell.xpath("(.//autocell)/text()")
						if '1' in autocells:			# Cell is a wordlist cell
							existing_wordlist = True
						else:	
							tt = ''.join(cell.xpath("(.//caption)/text()"))
							style = ''.join(cell.xpath(".//stylepreset/text()"))
							command_id = cell.xpath(".//id/text()")                 # Check the /Paramter/ID value to check if 'type' - i.e. being sent to the text bar.
	## NOT PERFECT - need to grab text sent to text bar rahter than caption...
							if ("type" in command_id or "speaknow" in command_id) and ("jump.to" not in command_id) and ("jump.back" not in command_id):    # We are only interested if text is being sent to the text bar or being spoken directly. We are not interested in jump cell text.
							#if tt != '':                                           # UNCOMMENT TO INCLUDE ALL CELLS WITH A CAPTION.
								if style not in blackliststyles:
	# Implement white list too?
									if  tt not in ignorecells:
										if ''.join(cell.xpath(".//hidden/text()")) != '1':
											cellchildren = cell.getchildren()
											vocabtext = picture = ''
											for cellchild in cellchildren:
												# Check if the cell has a type of speak command and if so save the text(s).
												commands = cellchild.getchildren()
												for command in commands:
													id = command.find("id")
													if id is not None:
														if id.text == "type" or "speaknow":
															parameters = command.findall("parameter")
															for parameter in parameters:
																if "1" in parameter.xpath(".//@index"):                                
																	vocabtext = parameter.text.strip()          # Grid seems to add Asquiggle charchters to the text if there is a space in the text output. Luckily python strip ditches them!
																	if(outputwordlists and len(vocabtext)>word_length and vocabtext !=[]  and re.match("[A-Za-z]", vocabtext)):  
																	# Ignore writing if no text, or text is smaller than min word size, or text is not letters.
																		word = etree.SubElement(wordlist, "word")
																		wordtext = etree.SubElement(word, "wordtext")
																		wordtext.text = etree.CDATA(vocabtext)
																		# Check if the cell has a picture (symbol) and if so save the picture path.
																		picture = ''.join(cell.xpath(".//picture/text()"))
																		if ((readpictures==True) and (picture != [])):   # ignore if no picture 
																			if(outputwordlists):
																				picturefile = etree.SubElement(word, "picturefile")
																				picturefile.text = picture
																			if (outputcsv):
																				vocabWriter.writerow([pth,cell.get('x'),cell.get('y'),vocabtext,picture])

					# Add in data from any existing wordlists! 
					if existing_wordlist == True and merge_lists==True:
						wordlistpath = os.path.dirname(pth) + "\wordlist.xml" 
						if os.path.isfile(wordlistpath):                # wordlist exists for this grid and is referenced in the grid. Need to add the wordlist data to the uber wordlist.
							wordlistwordlist = etree.parse(wordlistpath)
							root = wordlistwordlist.getroot()
							
							for wordx in root.iterfind("word"):     # MORE EFFICIENT METHOD???
								if outputwordlists:
									wordlist.append(wordx)          # HOW TO MAKE IT CDATA?
								if outputcsv:
									vocabWriter.writerow([pth,"wordlist","wordlist",str(wordx.findtext("wordtext")),str(wordx.findtext("picturefile"))])

######### ******* Write out data to many files ********** ###########
					if(singlefile == False):
						if(wordlist.findall('./word/')!=[]):				 # Do not write wordlists if they are blank.
							if (existing_wordlist==False or (existing_wordlist==True and merge_lists==True)): # Do not write worlists if there is a current list and not set to merge
								if(outinplace):
									if(outputwordlists):
										# Writing multiple files to Grid folders
										file_out = open( outputpath + 'wordlist.xml', 'wb')
										file_out.write('<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(wordlist, pretty_print=True, encoding='utf-8'))
								else:
									if(outputwordlists):
										# writing multiple files to output folder (make a folder for the grids, name them by the page).
										try:
											os.mkdir(outputpath + '/'+ gridsetname)
										except OSError, e:
											if e.errno != errno.EEXIST:
												raise
										file_out = open(outputpath + '/' + gridsetname + '/' + page +'.xml', 'wb')
										file_out.write('<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(wordlist, pretty_print=True, encoding='utf-8'))

########## ******** Write out to a single file after itterating the loop ******** ########
	if(singlefile == True):
		if(outputwordlists):
			file_out.write('<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(wordlist, pretty_print=True, encoding='utf-8'))

		  
						
						
def usage():
	print """
	This program takes a Grid 2 User folder and spits 
	out seperate CSV files full of the vocab in the grids
	
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
	-w, --wordlists     - Output wordlists
	-s, --singlefile    - single file wordlist output into one file?  Otherwise, will write to seperate files (in the name of the grid)

	Example Usage:
	ConvertGridtoWordLists.py --userdir="Path\To\Your\Grid2\User\Folder"  --output="Path\To\Dump\Output" -w

	
	Requirements:
	Python 2.3, Lxml, unicodecsv
	
	Author:
	Will Wade, will@e-wade.net
	"""              
					
def main():
	gridxml='grid.xml'
	outputpath ='.'
	userdir='.'
	excludehidden=False
	outputwordlists=False
	ignoregrids=[]
	ignorecells=[]
	blackliststyles=[]
	singlefile=False
	outputcsv=False
#    rewritegrids=False


	try:
		opts, args = getopt.getopt(sys.argv[1:], "houcgbxwsdv", ["help", "output=", "userdir=","ignorecells=","ignoregrids=", "blackliststyles=","excludehidden","wordlists", "singlefile", "dataascsv"])
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
		elif o in ("-w", "--wordlists"):
			outputwordlists = True
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
		elif o in ("-s", "--singlefile"):
			singlefile = True
		elif o in ("-d", "--dataascsv"):
			outputcsv = True

		else:
			assert False, "unhandled option"
	
	parse_grids(gridxml,outputpath,userdir,excludehidden,outputwordlists, ignoregrids, ignorecells, blackliststyles, singlefile, outputcsv)
# gridxml,outputpath,userdir,excludehidden,outputwordlists, ignoregrids, ignorecells, singlefile

if __name__ == "__main__":
	main()