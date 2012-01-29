#!/usr/bin/env python
# -*- coding: cp1252 -*-
# Contact: Will Wade <will@e-wade.net>
# Date: Jan 2012

# -*- coding: iso-8859-15 -*-

""" Grid Hacker.
- Export Grids as CSV files for analysis. Seperate files or One file. set location of where
- Export grids as wordlist files - pass flag to rewrite all the grids as wordlist Grids
 (NB Pass the -excludecommon and -excludewords to exclude common and your own wordlists to convert. Useful for template pages)
- Convert symbol-system. Will take the word. Look up in the image dictionary the closest symbol and rewrite any following licenced symbol area. 
"""
import pdb
import os.path, re
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
                ignoregrids=[],ignorecells=[], singlefile=False, outputcsv=False):
# gridxml,outputpath,userdir,excludehidden,outputwordlists, ignoregrids, ignorecells, singlefile, outputcsv
    '''
    Parse Grid.xml files recursively. Extract Vocabulary and store it out as CSV files and/or as Wordlist files
    '''

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
            gridsetname =  os.path.split(os.path.normpath(userdir))[1]
            file_out = open(outputpath +  gridsetname +'.xml', 'wb')
            wordlist = etree.Element("wordlist")
        if(outputcsv):
            vocabWriter = UnicodeWriter(open(outputpath + 'vocab.csv', 'wb'), delimiter=',', quotechar='"')
    
    for r,d,f in os.walk(userdir):                                  # Parse any directory, only picking up on grid.xml files.
        page = os.path.split(r)[1]
        if page not in ignoregrids:
            for files in f:
                if files.endswith("grid.xml"):
                    pth = os.path.join(r,files)
                    
                    if (outinplace):                                # Check to see if output directory specified, if not output to the Grid directories.
                        outputpath = r + '/'
                    tree = etree.parse(pth)                         # Parse the file
                    if(tree.xpath(".//licencekey") == []):          # does it have a licencekey? Bugger if it has 
## NOT SURE ABOUT THIS TEST... ???? SJ
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
                        tt = ''.join(cell.xpath("(.//caption)/text()"))
                        command_id = cell.xpath(".//id/text()")                 # Check the /Paramter/ID value to check if 'type' - i.e. being sent to the text bar.
## NOT PERFECT - need to grab text sent to text bar rahter than caption...
                        if "type" in command_id or "speaknow" in command_id:    # We are only interested if text is being sent to the text bar or being spoken directly.
                        #if tt != '':                                           # UNCOMMENT TO INCLUDE ALL CELLS WITH A CAPTION.
                            if  tt not in ignorecells:
                                if ''.join(cell.xpath(".//hidden/text()")) != '1':
                                    if(outputwordlists):
                                        word = etree.SubElement(wordlist, "word")
                                    cellchildren = cell.getchildren()
                                    vocabtext = picture = ''
                                    for cellchild in cellchildren:
                                        # Check if the cell has a type of speak command and if so save the text(s).
                                        commands = cellchild.getchildren()
                                        for command in commands:
                                            id = command.find("id")
                                            if id.text == "type" or "speaknow":
                                                parameters = command.findall("parameter")
                                                for parameter in parameters:
                                                    if "1" in parameter.xpath(".//@index"):                                
                                                        vocabtext = parameter.text.strip()          # Grid seems to add Asquiggle charchters to the text if there is a space in the text output. Luckily python strip ditches them!
                                                        if(outputwordlists):
                                                            wordtext = etree.SubElement(word, "wordtext")
                                                            wordtext.text = etree.CDATA(vocabtext)
                                                # Check if the cell has a picture (symbol) and if so save the picture path.
                                                picture = ''.join(cell.xpath(".//picture/text()"))
                                                if ((readpictures==True) and (picture != [])):
                                                    if(outputwordlists):
                                                        picturefile = etree.SubElement(word, "picturefile")
                                                        picturefile.text = picture
                                                if (outputcsv):
                                                    vocabWriter.writerow([pth,cell.get('x'),cell.get('y'),vocabtext,picture])

                    if(singlefile == False):
                        if(outinplace):
                            if(outputwordlists):
                                # Writing multiple files to Grid folders
                                file_out = open( outputpath + 'wordlist.xml', 'wb')
                                file_out.write('<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(wordlist, pretty_print=True, encoding='utf-8'))
                        else:
                            if(outputwordlists):
                                # writing multiple files to output folder
                                file_out = open(outputpath + page +'.xml', 'wb')
                                file_out.write('<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(wordlist, pretty_print=True, encoding='utf-8'))

    # Write out to a single file after itterating the loop
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
    -g, --ignoregrids=   - Exclude grids listed from a text file (e.g, back, jump)
    -x, --excludehidden - Exclude hidden cells from the analysis
    -w, --wordlists     - Output wordlists
    -s, --singlefile    - single file wordlist output into one file?  Otherwise, will write to seperate files (in the name of the grid)
    
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
    singlefile=False
    outputcsv=False
#    rewritegrids=False


    try:
        opts, args = getopt.getopt(sys.argv[1:], "houcgxwsdv", ["help", "output=", "userdir=","ignorecells=","ignoregrids=","excludehidden","wordlists", "singlefile", "dataascsv"])
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
        elif o in ("-s", "--singlefile"):
            singlefile = True
        elif o in ("-d", "--dataascsv"):
            outputcsv = True

        else:
            assert False, "unhandled option"
    
    parse_grids(gridxml,outputpath,userdir,excludehidden,outputwordlists, ignoregrids, ignorecells, singlefile, outputcsv)
# gridxml,outputpath,userdir,excludehidden,outputwordlists, ignoregrids, ignorecells, singlefile

if __name__ == "__main__":
    main()
