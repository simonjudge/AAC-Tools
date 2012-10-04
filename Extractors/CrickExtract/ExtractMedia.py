#!/usr/bin/env python 2.7
# Contact: Will Wade <will@e-wade.net> 
# Date: March 2012

"""
Read a clicker grid
Export in same folder all the embeded sounds, video and images
  
##Binary##
http://dl.dropbox.com/u/66960/Apps/ExtractMediaFromClicker5.zip

##Code##
https://gist.github.com/2127181

##Credits##
Amy B

##Usage##
Simply drop your .clkx file ontop of the ExtractMediaFromClicker.exe file. 
A bunch of sound and image files will then be extracted and saved to the same directory of your clicker file

NB: THIS HAS BEEN DESIGNED TO ASSIST GRABBING LONG LOST MEDIA FILES EMBEDDED IN CLICKER FILES
SOME CLICKER GRIDS ARE PAID-FOR GRIDS WITH COPYRIGHTED MATERIAL. PLEASE DONT USE THIS TOOL TO EXTRACT AND REUSE
SUCH PAID FOR CONTENT!!

##Caveats##

- You may need to move the clicker file somewhere writeable - e.g. it may struggle to write to networked drives. 
- If you lose any files don't blame me - to be safe copy the clicker file to a new folder and drag and drop there. 
- It will only extract embedded files. 

  
##to build##
   install python up to python 2.7 (python.org)
   use py2exe for correct build of python: http://www.lfd.uci.edu/~gohlke/pythonlibs/#py2exe
   use a  setup.py as very last example here: http://py2exe.org/index.cgi/SingleFileExecutable

##tips##
    rm *.png *.PNG *.JPG *.jpg *.wav *.bmp
"""

# -*- coding: iso-8859-15 -*-


from xml.etree.ElementTree import ElementTree
import base64, sys, os 

try:
    filename = sys.argv[1]
    print "opening",sys.argv[1]
    filen,ext = filename.split(os.extsep)
    if ext == 'clkx' or ext == 'clkk' or ext == 'clkt':
        tree = ElementTree()
        tree.parse(filename)
        i = 1
        for atype in tree.findall('crickdata/sound'):
            if atype.get('link') == 'Embed':
                filename = atype.get('name', str(i)) + '.'+ atype.get('filetype')
                print 'Writing: '+filename
                f = open(filename, 'w')
                f.write(base64.b64decode(atype.find('base64').text))
                f.close()
                i=i+1            
        
        for pitype in tree.findall('crickdata/pic'):
            iname = pitype.get('name','None')
            for ptype in pitype.findall('picdata'):    
                if ptype.get('link') == 'Embed':
                    if iname == 'None':
                        imagename = ptype.get('name',ptype.get('state','Unknown')+str(i)) + '.' +  ptype.get('filetype')
                    else:
                        imagename = iname+'-'+ptype.get('state','Unknown')+str(i) + '.' +  ptype.get('filetype')
                    print 'Writing: '+imagename
                    f = open(imagename, 'w')
                    f.write(base64.b64decode(ptype.find('base64').text))
                    f.close()
                    i=i+1
    else:
        print "whoops. Doesnt look like a clicker file"
        exit()
except IndexError:
    print "usage:",sys.argv[0].split("\\")[-1],"FILE"
    exit()
except IOError as (errno, strerror):
    print "I/O error({0}): {1}".format(errno, strerror)
    exit()

