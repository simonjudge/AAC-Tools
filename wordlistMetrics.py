#!/usr/bin/env python
# Contact: Will Wade <will@e-wade.net> / Simon Judge
# Date: Jan 2012

# -*- coding: iso-8859-15 -*-

""" Wordlist Metrics.
"""
import os.path, re
from lxml import etree
import getopt, sys, csv
from sets import Set
import nltk
from unicodecsv import UnicodeWriter  

import pdb

# I think we may need set
def countDuplicatesInList(dupedList):
   uniqueSet = Set(item for item in dupedList)
   return [(item, dupedList.count(item)) for item in uniqueSet]

def uniqueSet(dupedList):
    uniqueSet = Set(item for item in dupedList)
    return uniqueSet

def parse_wordlist(wordlistxml='wordlist.xml', outputpath='.'):
    '''
    Parse wordlist.xml file. Just do the big one for now
    '''
    linguistics_out = UnicodeWriter(open(outputpath + 'linguistic-metrics.csv', 'wb'), delimiter=',', quotechar='"')
    linguistics_out.writerow(["WORD", "COUNT", "TYPE"])

    tree = etree.parse(wordlistxml)
    #Ok many ways to do this
    allwords = tree.xpath("(//wordlist//word//wordtext)/text()")
    
    # how many times is a word/phrase mentioned?     
    uniqueWords = uniqueSet(allwords)              # Set of unique words.
    pdb.set_trace()
   # Output metrics to file.
    for item in uniqueWords:
       linguistics_out.writerow([item, str(allwords.count(item)), nltk.pos_tag(item)[-1][-1]])
   

def usage():
    print """
    This program takes a Grid 2 wordlist file
    
    Flags:
    -h, --help          - This screen
    -v                  - Verbose (debug)
    -w, --wordlist      - File path of wordlist.xml
    -o, --output        - Directory to store output csv
    
    Requirements:
    Python 2.3, Lxml, unicodecsv
    
    Author:
    Will Wade, will@e-wade.net
    Simon Judge 
    """              
                    
def main():
    wordlistxml='wordlist.xml'
    outputpath ='.'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hwo:v", ["help","wordlist=", "output="])
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
        elif o in ("-w=", "--wordlist"):
            if os.path.exists(os.path.normpath(a)):
                wordlistxml = os.path.normpath(a)
            else:
                assert False, "non-existent wordlistfile: " + os.path.normpath(a)
        elif o in ("-o=", "--output"):
            if os.path.exists(os.path.normpath(a) + '/'):
                outputpath = os.path.normpath(a) + '/'
            else:
                assert False, "non-existent output csv directory: " + os.path.normpath(a)               
        else:
            assert False, "unhandled option"

    
    parse_wordlist(wordlistxml, outputpath)

if __name__ == "__main__":
    main()
