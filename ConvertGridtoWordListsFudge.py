## Tool to convert cells in a grid set into a WordList.
## MORE HELP...

## TO DO:
##  - Distinguish between the cells with vocab and non vocab - this is why itterating over cells, as well as captions.
##  - Check RE CDATA. 

import os.path, re
from string import Template
import Tkinter, tkFileDialog
from elementtree import ElementTree

## GET FILENAME OF DIR
root = Tkinter.Tk()
dirname = tkFileDialog.askdirectory(parent=root,initialdir=os.environ['ALLUSERSPROFILE'],title='Please select the GridSet directory')
print dirname
root.destroy()

pattern = re.compile("<caption><!\[CDATA\[([!#$%&'()*+,./:;<=>?@\^_`{|}\w ]+)\]\]><\/caption>")
s = Template("'$data',")

if len(dirname ) > 0:
    for r,d,f in os.walk(dirname):
        for files in f:
            # Itterate over all the grid.xml files in the directory and sub directories
            if files.endswith("grid.xml"):
                pth = os.path.join(r,files)

                treein = ElementTree.ElementTree()
                treein.parse(pth)
                cells = treein.getiterator('cell')

                wordlist = ElementTree.Element("wordlist")

                print pth
                
                for cell in cells:
                ## Itterate over all the cells.
                ## TODO: Distinguish between the cells with vocab and non vocab - this is why itterating over cells, as well as captions.
                    captions = cell.getiterator('caption')
                    for caption in captions:
                        print caption.text

                        word =ElementTree.SubElement(wordlist, "word")
                        wordtext = ElementTree.SubElement(word, "wordtext")
#                       wordtext.text = "<![CDATA[ " + caption.text +" ]]>"
## THERE IS AN ISSUE WITH PARSING CDATA AS XML, LUCKILY THIS DOESN'T SEEM ESSENTIAL TO THE GRID2 SCHEMA.
                        wordtext.text = caption.text
                        picture = ElementTree.SubElement(word, "picturefile")
                        picture.text = cell.find('picture').text

                outputfile = open(os.path.join(r,"wordlist.xml"), "w+")
                outputfile.write('<?xml version="1.0" encoding="UTF-8"?>' + ElementTree.tostring(wordlist, 'utf-8'))             
                outputfile.close()
                         
