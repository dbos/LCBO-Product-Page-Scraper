#!/usr/bin/python2.7
################################################################################
#Author: Danny O'Sullivan (danny.osullivan@gmail.com)
#
#Depends:wineObject
#
#Description: Basically this is just a script that when given a CSPC on the 
#command line, it will look up a bunch of details on the LCBO printer-friendly
#product page and return it to stdout as fields delimited by the "|" character
#
#Usage: python lcboonelookup.py 216 (would look up cspc 216) 
################################################################################
import sys
import codecs
import wineObject
import re
import csv
from wineObject import wineObjectClass

x=wineObjectClass(sys.argv[-1])
if not x.fail:
    print (x.image)
