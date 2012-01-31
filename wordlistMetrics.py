#!/usr/bin/env python
# Contact: Will Wade <will@e-wade.net> / Simon Judge
# Date: Jan 2012

# -*- coding: iso-8859-15 -*-

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
    lsummary_out = UnicodeWriter(open(outputpath + 'linguistic-metrics.csv', 'wb'), delimiter=',', quotechar='"')
    lsummary_out.writerow(["File Name", "Total Words or Phrases", "Total Unique Words or Phrases", "Total Words", "Total Phrases", "Total Unique Words", "Total Unique Phrases", "Types of Word"])
    donedirs = []
    uwords = []
    word_types = []
    wordtypes =[]
    phrases =[]
    uphrases =[]
    allwords = []

    total_wordsphrases = total_uwordsphrases = total_words = total_phrases = 0

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
                        
                    ldata_out = UnicodeWriter(open(outputpath + '/'+ gridset +'/language-data.csv', 'wb'), delimiter=',', quotechar='"')
                    ldata_out.writerow(["WORD", "NUMBER OF WORDS", "COUNT", "TYPE"])
                    
                    if len(donedirs)>1:                                 # Write raw data and summary data after recursing a directory.  
                        
                        uniqueWords = uniqueSet(allwords)              # Set of unique words.
                       # Output metrics to file.
                        for item in uniqueWords:
                           num_words = len(item.split())
                           item_count = allwords.count(item)
                           if num_words == 1:                          # Single word
                              word_type = nltk.pos_tag(item)[-1][-1]
                              ldata_out.writerow([item, str(num_words), str(item_count), word_type])
                              words.append(item)
                              wordtypes.append(word_type)
                           elif num_words > 1:                         # Phrase
                              nltk_words = nltk.word_tokenize(item)
                              word_pos = nltk.pos_tag(nltk_words) ### HOW TO DEAL WITH PHRASES???
                              word_types = [x[1] for x in word_pos]
                              ldata_out.writerow([item, str(num_words), str(item_count), " ,".join(word_types)])
                    # HOW TO OUTPUT EACH POS TO A COLUMN???
                              phrases.append(item)

                        uword_types = countDuplicatesInList(wordtypes)
                        total_wordsphrases = len(allwords)
                        total_uwordsphrases = len(uniqueWords)
                        total_words = len(words)
                        total_phrases = len(phrases)
                        
                        lsummary_out.writerow([donedirs[-2], str(total_wordsphrases), str(total_uwordsphrases), str(total_words), str(total_phrases), ', '.join(map(str, uword_types))])
                        total_wordsphrases = total_uwordsphrases = total_words = total_phrases = 0

                        raw_words_out = open(outputpath + '/'+ donedirs[-2] +'/raw-words.text', 'wb')
                        raw_words_out.writelines('\n'.join(words))
                        raw_phrases_out = open(outputpath + '/'+ donedirs[-2] +'/raw-phrases.txt', 'wb')
                        raw_phrases_out.writelines('\n'.join(phrases))
                        
                        words = []
                        word_types = []
                        wordtypes =[]
                        phrases =[]
                        allwords = []

                tree = etree.parse(filepth)
                #Ok many ways to do this
                allwords += tree.xpath("(//wordlist//word//wordtext)/text()")
                # how many times is a word/phrase mentioned?

                ############# WRITE AT END OF DIR.
    
 
    # Write data out for the last folder (gridset) encountered - MUST BE A BETTER WAY THAN THIS?
    uniqueWords = uniqueSet(allwords)              # Set of unique words.
   # Output metrics to file.
    for item in uniqueWords:
       num_words = len(item.split())
       item_count = allwords.count(item)
       if num_words == 1:                          # Single word
          word_type = nltk.pos_tag(item)[-1][-1]
          ldata_out.writerow([item, str(num_words), str(item_count), word_type])
          uwords.append(item)
          wordtypes.append(word_type)
       elif num_words > 1:                         # Phrase
          nltk_words = nltk.word_tokenize(item)
          word_pos = nltk.pos_tag(nltk_words) ### HOW TO DEAL WITH PHRASES???
          word_types = [x[1] for x in word_pos]
          ldata_out.writerow([item, str(num_words), str(item_count), " ,".join(word_types)])
# HOW TO OUTPUT EACH POS TO A COLUMN???
          phrases.append(item)

    uphrases = uniqueSet(phrases)
    uword_types = countDuplicatesInList(wordtypes)
    
    total_wordsphrases = len(allwords)
    total_uwordsphrases = len(uniqueWords)
    total_words = len(allwords)
    total_phrases = len(phrases)
    total_uwords = len(uwords)
    total_uphrases = len(uphrases)
    
    
    lsummary_out.writerow([gridset, str(total_wordsphrases), str(total_uwordsphrases), str(total_words), str(total_phrases), str(total_uwords), str(total_uphrases), ', '.join(map(str, uword_types))])

    raw_words_out = open(outputpath + '/'+ gridset +'/raw-unique-words.text', 'wb')
    raw_words_out.writelines('\n'.join(uniqueWords))
    raw_phrases_out = open(outputpath + '/'+ gridset +'/raw-unique-phrases.txt', 'wb')
    raw_phrases_out.writelines('\n'.join(uphrases))
    raw_words_out = open(outputpath + '/'+ gridset +'/raw-words.text', 'wb')
    raw_words_out.writelines('\n'.join(allwords))
    raw_phrases_out = open(outputpath + '/'+ gridset +'/raw-phrases.txt', 'wb')
    raw_phrases_out.writelines('\n'.join(phrases))
    
    words = []
    word_types = []
    wordtypes =[]
    phrases =[]


    
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
