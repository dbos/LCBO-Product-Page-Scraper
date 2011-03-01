import sys
import codecs
import wineObject
import re
import csv
from wineObject import cspclook
#I think when I wrote this I was confused about encodings. I don't want to change anything now though since it seems to work. 
encod="ISO-8859-1"
x=wineObject.wineObjectClass(cspclook(sys.argv[-1]).decode(encod),int(sys.argv[-1])) #takes argument from command line
a=[x.name.encode(encod),x.cspc,x.price,x.ptype.encode(encod),x.sugar,x.bottlesize,x.country.encode(encod),x.producer.encode(encod),x.save,x.airmiles,x.until,x.VQA,x.description.encode(encod),x.alcohol.encode(encod)]
print ("|".join(map(str,a))) #The standard for the filemaker side of things is for fields to be delimited in this way.
