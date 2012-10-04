#!/usr/bin/env python
# Contact: Will Wade <will@e-wade.net> / Simon Judge
# Date: Jan 2012

# -*- coding: iso-8859-15 -*-

# Utils
import sys
sys.path.append('../utils')

""" Wordlist Metrics.
"""
import os.path, errno,re
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

def parse_wordlist(wordlistdir='.', outputpath='.', anyxml = False):
# MOVE THIS INITIALISATION TO IN THE FOR LOOOP TO AVOID BLANK FILES AT END. TEST.
    lsummary_out = UnicodeWriter(open(outputpath + 'linguistic-metrics.csv', 'wb'), delimiter=',', quotechar='"')
    lsummary_out.writerow(["File Name", "Total Words or Phrases", "Total Unique Words or Phrases", "Total Words", "Total Phrases", "Total Unique Words", "Total Unique Phrases", "Types of Word"])
    donedirs = []
    allwordsphrases = []
    gridset = ''

    for r,dirs,files in os.walk(wordlistdir):                  # Parse any directory, picking up on either wordlist.xml or any xml files (USE with CARE)!
        for filename in files:                                      # Assume that xml files are organised in directories according to the Gridset. Will not currently work when parsing Grid user folders (it will do the stats per page)
            if (anyxml == True and filename.endswith(".xml")) or (anyxml == False and filename.endswith("wordlist.xml")):
                
                filepth = os.path.join(r,filename)
                gridset = os.path.normpath(filepth).split(os.sep)[-2]
              
                if gridset not in donedirs:                              # Got to new directory. MUST BE BETTER WAY OF DOING THIS!!!
                    donedirs.append(gridset)
                    try:                                                 # Make directory to output raw data.
                        os.mkdir(outputpath + '/'+ gridset )
                    except OSError, e:
                        if e.errno != errno.EEXIST:
                            raise
                                            
                    if len(donedirs)>1:
                        writeOut(lsummary_out, allwordsphrases, outputpath, donedirs[-2])    # Write raw data and summary data after recursing a directory.
                        allwordsphrases = []

                tree = etree.parse(filepth)
                allwordsphrases += tree.xpath("(//wordlist//word//wordtext)/text()")
    
    writeOut(lsummary_out, allwordsphrases, outputpath, gridset)    # Write raw data and summary data of last directory.

def writeOut(lsummary_out, allwordsphrases=[],  outputpath='.', gridset=''):    
 
    # Write data out for the last folder (gridset) encountered - MUST BE A BETTER WAY THAN THIS?
    uWordsPhrases = uniqueSet(allwordsphrases)              # Set of unique words.
    uwords =[]
    uphrases = []
    words = []
    phrases =[]
    wordtypes =[]
    wordtypes =[]
    total_wordsphrases = total_uwordsphrases = total_words = total_phrases = 0

    ldata_out = UnicodeWriter(open(outputpath + '/'+ gridset +'/language-data.csv', 'wb'), delimiter=',', quotechar='"')
    ldata_out.writerow(["WORD", "NUMBER OF WORDS", "COUNT", "TYPE"])
    
   # Output metrics  to file.
    for item in uWordsPhrases:
       num_words = len(item.split())
       item_count = allwordsphrases.count(item)
       if num_words == 1:                          # Single word
          word_type = nltk.pos_tag(item)[-1][-1]
          #word_type_help = nltk.help.upenn_tagset(word_type)
# MAYBE CONVERT TAGS INTO MORE USEFUL WORDS?!
          ldata_out.writerow([item, str(num_words), str(item_count), word_type])
          uwords.append(item)
          wordtypes.append(word_type)
       elif num_words > 1:                         # Phrase
          nltk_words = nltk.word_tokenize(item)
          word_pos = nltk.pos_tag(nltk_words) ### HOW TO DEAL WITH PHRASES???
          word_types = [x[1] for x in word_pos]
          ldata_out.writerow([item, str(num_words), str(item_count), " ,".join(word_types)])
# HOW TO OUTPUT EACH POS TO A COLUMN???
          uphrases.append(item)

    for item in allwordsphrases:
        num_words = len(item.split())
        if num_words == 1:
            words.append(item)
        elif num_words > 1:
            phrases.append(item)
        
    uword_types = countDuplicatesInList(wordtypes)
    
    total_wordsphrases = len(allwordsphrases)
    total_uwordsphrases = len(uWordsPhrases)
    total_uwords = len(uwords)
    total_uphrases = len(uphrases)

    total_words = len(words)
    total_phrases = len(phrases)
    
    #["File Name", "Total Words or Phrases", "Total Unique Words or Phrases", "Total Words", "Total Phrases", "Total Unique Words", "Total Unique Phrases", "Types of Word"])
    lsummary_out.writerow([gridset, str(total_wordsphrases), str(total_uwordsphrases), str(total_words), str(total_phrases), str(total_uwords), str(total_uphrases), ', '.join(map(str, uword_types))])

    raw_words_out = open(outputpath + '/'+ gridset +'/raw-unique-words.text', 'wb')
    raw_words_out.writelines('\n'.join(uWordsPhrases).encode('utf-8'))
    raw_phrases_out = open(outputpath + '/'+ gridset +'/raw-unique-phrases.txt', 'wb')
    raw_phrases_out.writelines('\n'.join(uphrases).encode('utf-8'))
    raw_words_out = open(outputpath + '/'+ gridset +'/raw-wordsphrases.text', 'wb')
    raw_words_out.writelines('\n'.join(allwordsphrases).encode('utf-8'))

    

    
def usage():
    print """
    This program takes a Grid 2 wordlist file and outputs the raw words, phrases and some stats.
    The program will find either wordlist.xml or any .xml files in the directory provided. Data will be output by folder - i.e. one row of stats per folder of wordlist files.
    This program will not currently parsing Grid user folders directly - it is designed to be used with the Convert grids to wordlists programme.
    
    Flags:
    -h, --help          - This screen
    -v                  - Verbose (debug)
    -w, --wordlistdir   - Folder path of wordlist.xml or xml files to scan.
    -o, --output        - Directory to store output csv
    -a                  - Search for ANY xml file, not just wordlist.xml
    
    e.g.
    python wordlistMetrics.py --wordlistdir="../temp/IDV/" --output="../output/"
    
    Requirements:
    Python 2.3, Lxml, unicodecsv
    
    Author:
    Will Wade, will@e-wade.net
    Simon Judge 
    """              
                    
def main():
    wordlistdir='.'
    outputpath ='.'
    anyxml = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hwoav", ["help","wordlistdir=", "output="])
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
        elif o in ("-w=", "--wordlistdir"):
            if os.path.exists(os.path.normpath(a)):
                wordlistdir = os.path.normpath(a)
            else:
                assert False, "non-existent wordlistfile: " + os.path.normpath(a)
        elif o in ("-o=", "--output"):
            
            if os.path.exists(os.path.normpath(a) + '/'):
                outputpath = os.path.normpath(a) + '/'
            else:
                assert False, "non-existent output csv directory: " + os.path.normpath(a)               
        elif o == "-a":
            anyxml = True
        else:
            assert False, "unhandled option"

    
    parse_wordlist(wordlistdir, outputpath, anyxml)

if __name__ == "__main__":
    main()