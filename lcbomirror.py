#################################################################################
#Author: Danny O'Sullivan
#
#Depends:MySQLdb
#
#Description: A short little script that stores most of the data (in SQLite) from
#	the lcbo product pages for each CSPC listed in activeproducts.txt
#Usage: Call from command line. Output database is lcbomirror.db
#Input file format: The input file is a file called "activeproducts.txt" which is
#	just a file with CSPCs seperated by line breaks. Leading 0s don't matter.
#	One could obtain this file with:
#		cat activeproductsXX.dat | cut -c 1-7 > activeproducts.txt
#################################################################################

num_lines = sum(1 for line in open('activeproducts.txt'));
f=open('activeproducts.txt','r');
g=open('done.log','w');
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
	if (x.name != "unknown"):
		cursor.execute("INSERT INTO lcbo_productlist VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
				(tempcspc,
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
			x.description))
		g.write(str(tempcspc)+"\n")
#Commits every 100 records, or when finished
	if (count % 100 == 0):
		conn.commit()

conn.commit()
f.close();
cursor.close()
