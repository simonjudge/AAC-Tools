#!/usr/bin/env python
# -*- coding: cp1252 -*-
# Contact: Will Wade <will@e-wade.net>
# Date: Jan 2012

# Convert folder of images to a sqllite database so can use it for symbol lookups

import os.path, getopt, sys, sqlite3

def parse_images(imagedir, sqlitefile, symbolset):
    SQLInsert = ''
    a = 1;
    for r,d,f in os.walk(imagedir):     
        for n in f:
            # SymmbolName: strip .emf, .wmf, .png .jpg .jpeg, from file
            #   replace _ - with SPACE             
            SymbolName = os.path.splitext(n)[0]
            # keywords = file path words (minus numbers and any 7-7 pattern) plus SymbolBane             
            parts = r[len(imagedir):].split('/')
            partsTxt = ','.join(parts)
            SQLInsert = SQLInsert + 'INSERT INTO ss' + symbolset +' VALUES ('+str(a)+',"'+SymbolName+'","'+r+'/'+n+'","'+ partsTxt +'"); '
            a=a+1
    try:
        connection = sqlite3.connect(sqlitefile)
        cur = connection.cursor()  
        cur.executescript(SQLInsert)
        connection.commit()
        print str(a)+" images inserted into ss"+symbolset+" of "+sqlitefile
    
    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)
                
    
def setup_db(sqlitefile, symbolset):
    try:
        connection = sqlite3.connect(sqlitefile)
        cur = connection.cursor()  
        cur.executescript('DROP TABLE IF EXISTS ss' + symbolset +';' +
            'CREATE TABLE ss' + symbolset +'(Id INTEGER PRIMARY KEY, SymbolName TEXT, Path TEXT, Keywords TEXT);')
        connection.commit()
        
    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)


def usage():
    print """
    This program takes a directory of images and builds a sqllite database from the images
    To then be used in other AAC Tools
    NB: deletes the Table each time. Be careful to name your SymbolSet properly
    
    Flags:
    -h, --help          - This screen
    -v                  - Verbose (debug)
    -i, --imagedir=      - File path of the image Folder you want to analyse
    -s, --symbolset=     - Name of the symbolset (NB: No spaces or funny Characters please!)
    -d, --database=      - Name of the sqlite database 
    

    Example Usage:
    SymbolCollector.py --imagedir="Path\To\Your\Image\Folder"  --symbolset=Widgit -database="SymbolCollector.db" 
    
    Requirements:
    Python 2.3, Lxml, unicodecsv
    
    Author:
    Will Wade, will@e-wade.net
    """              


def main():
    imagedir='.'
    sqlitefile ='SymbolCollector.db'
    symbolset='Widgit'

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hivsd", ["help", "imagedir=","sqlitefile=","symbolset=","database="])
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
        elif o in ("-s", "--symbolset"):
            symbolset = str(a)        
        elif o in ("-d", "--database"):
            sqlitefile = str(a)           
        elif o in ("-i", "--imagedir"):            
            if os.path.exists(os.path.normpath(a) + '/'):
                imagedir = os.path.normpath(a) + '/'
            else:
                assert False, "non-existent user directory: " + os.path.normpath(a) + '/'
        else:
            assert False, "unhandled option"
    
    setup_db(sqlitefile, symbolset)
    parse_images(imagedir, sqlitefile, symbolset)
    
if __name__ == "__main__":
    main()
