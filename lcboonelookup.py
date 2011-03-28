################################################################################
#Author: Danny O'Sullivan (danny.osullivan@gmail.com)
#
#Depends:wineObject
#
#Description: Basically this is just a script that when given a CSPC on the 
#command line, it will look up a bunch of details on the LCBO printer-friendly
#product page and return it to stdout as fields delimited by the "|" character
#right now, it is called from filemaker using applescript, and output is used 
#by a custom function in a filemaker database to split it into bonafide fields.
#
#Usage: python lcboonelookup.py 216 (would look up cspc 216) 
################################################################################
import sys
import codecs
import wineObject
import re
import csv
from wineObject import cspclook

#I think when I wrote this I was confused about encodings. I was jumping back and 
#forth between 2.7 and 3, and was confused about how it was implemented in each
#I don't want to change anything now though since it seems to work. 
encod="ISO-8859-1"

x=wineObject.wineObjectClass(cspclook(sys.argv[-1]),int(sys.argv[-1]))
a=[x.name,
		x.cspc,x.price,
		x.ptype,
		x.sugar,x.bottlesize,
		x.country,
		x.producer,
		x.save,
		x.airmiles,
		x.until,
		x.VQA,
		x.description,
		x.alcohol]
print ("|".join(map(unicode,a)))
