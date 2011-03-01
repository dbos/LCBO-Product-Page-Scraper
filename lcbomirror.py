#################################################################################
#Author: Danny O'Sullivan
#
#Depends:MySQLdb
#
#Description: A short little script that stores most of the data (in MySQL) from
#	the lcbo product pages for each CSPC listed in activeproducts.txt
#Usage: Call from command line with mysql user, password, and db as arguments
#	eg: python lcbomirror.py fred luckypass mydb
#################################################################################

f=open('activeproducts.txt','r');
g=open('done.log','w');
import sys
if len(sys.argv) != 3:
	sys.stderr.write('Usage: python lcbomirror.py <user> <pass> <db> (with no brackets)')
import MySQLdb
conn=MySQLdb.connect(
		host = "localhost",
		user = sys.argv[1],
		passwd = sys.argv[2],
		db = sys.argv[3])
cursor=conn.cursor()

#Nothing really of interest except MySQL cursor usage maybe for reference
#All the real magic is in wineObject.py

import wineObject
from wineObject import cspclook
for line in f:
	tempcspc=line.strip().lstrip('0');
	print tempcspc
	x=wineObject.wineObjectClass(cspclook(tempcspc),tempcspc)
        cursor.execute ("INSERT INTO lcbo_productlist VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
			(int(tempcspc),
			str(x.name),
			str(x.producer),
			float(x.price),
			str(x.country),
			str(x.ptype),
			str(x.releaser),
			float(x.save),
			float(x.airmiles),
			str(x.until),
			str(x.sugar),
			str(x.alcohol),
			str(x.VQA),
			str(x.bottlesize),
			str(x.releasedate)))
	g.write(str(tempcspc)+"\n")
f.close();
cursor.close()
