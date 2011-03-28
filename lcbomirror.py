#################################################################################
#Author: Danny O'Sullivan
#
#Description: A short little script that stores most of the data (in SQLite) from
#	the lcbo product pages for each CSPC listed in activeproducts.txt
#	Also creates a csv file, webdatabase.csv
#Usage: Call from command line. 
#Output: Output db file is lcbomirror.db, Output csv file is webdatabase.csv
#Input file format: The input file is a file called "activeproducts.txt" which is
#	just a file with CSPCs seperated by line breaks. Leading 0s don't matter.
#	One could obtain this file with:
#		cat activeproductsXX.dat | cut -c 1-7 > activeproducts.txt
#################################################################################
import codecs
import csv
codec="iso-8859-1"
num_lines = sum(1 for line in open('activeproducts.txt'));
f=open('activeproducts.txt','r');
g=open('done.log','w');
h=open('webdatabase.csv',"w")
j=csv.writer(h,dialect='excel')
import sys
import sqlite3 
conn=sqlite3.connect('lcbomirror.db')
cursor=conn.cursor()
cursor.execute("""DROP TABLE lcbo_productlist""")
conn.commit()
cursor.execute("""CREATE TABLE lcbo_productlist (cspc,name,producer,price,country,ptype,releasaer,save,airmiles,until,sugar,alcohol,vqa,bottlesize,releasedate,description)""")

#Nothing really of interest except SQLite cursor usage maybe for reference
#All the real magic is in wineObject.py

import wineObject
from wineObject import cspclook
count=0;
for line in f:
	count+=1
	tempcspc=line.strip().lstrip('0');
	print str(count)+"  /  "+str(num_lines)+"  =  "+str(round(100*float(count)/float(num_lines),2))+"% completed";
	x=wineObject.wineObjectClass(cspclook(tempcspc),tempcspc)
	if (len(x.name) >1):
	#First I create a row for the sqlite query. sqlite supports unicode and dynamic types
		row=(tempcspc,
		x.name,
		x.producer,
		x.price,
		x.country,
		x.ptype,
		x.releaser,
		x.save,
		x.airmiles,
		x.until,
		x.sugar,
		x.alcohol,
		x.VQA,
		x.bottlesize,
		x.releasedate,
		x.description)
		cursor.execute("INSERT INTO lcbo_productlist VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",row)
	#Now I have to repeat this row nonsense, but manually encode string fields 
	#this is because csv.writer doesn't natively support unicode.
	#Also could create a sanitizing function for this and map with it.
		row=(tempcspc,
		x.name.encode('iso-8859-1'),
		x.producer.encode('iso-8859-1'),
		x.price,
		x.country.encode('iso-8859-1'),
		x.ptype.encode('iso-8859-1'),
		x.releaser.encode('iso-8859-1'),
		x.save,
		x.airmiles,
		x.until.encode('iso-8859-1'),
		x.sugar.encode('iso-8859-1'),
		x.alcohol.encode('iso-8859-1'),
		x.VQA,
		x.bottlesize.encode('iso-8859-1'),
		x.releasedate.encode('iso-8859-1'),
		x.description.encode('iso-8859-1'))
	#writes the successfully parsed CSPC to a log
		g.write(str(tempcspc)+"\n")
	#writes the csv record.
		j.writerow(row)
#Commits every 100 records, or when finished
	if (count % 100 == 0):
		conn.commit()

conn.commit()
f.close();
cursor.close()
