#The purpose of this script is to read in an activeproducts.txt file and store the distinct occurences of particular fields into a "conversion tables".
#The point was to convert the LCBO's notation on country/region and type/subtype fields on the product pages to VintageAssessments'
#takes database info from command line

#Depends on MySQLdb

f=open('activeproducts.txt','r');
g=open('done.tab','w');
import MySQLdb
import sys
conn=MySQLdb.connect(
		host = "localhost",
		user= sys.argv[1],
		passwd = sys.argv[2],
		db = sys.argv[3])
cursor=conn.cursor()
import wineObject
from wineObject import cspclook
for line in f:
	tempcspc=line.strip().lstrip('0');
	print tempcspc
	x=wineObject.wineObjectClass(cspclook(tempcspc),tempcspc)
        cursor.execute ("SELECT DISTINCT * from lcbo_typeconv WHERE name = %s",x.ptype)
	if cursor.fetchone() is None:
        	cursor.execute ("INSERT INTO lcbo_typeconv VALUES (%s,\" \")",str(x.ptype))
        cursor.execute ("SELECT DISTINCT * from lcbo_countryconv WHERE name = \""+ x.country+"\"")
	if cursor.fetchone() is None:
        	cursor.execute ("INSERT INTO lcbo_countryconv VALUES (%s,\" \")",str(x.country))
	g.write(str(tempcspc)+"\n")
f.close();
cursor.close()

#OK. So it reads in a ptype. If it's been seen before, it does nothing, if not, it adds it. Same thing for country. So do a select for it, if no result, do an add. Record the last CSPC used in case of error and loop until all CSPCs have been checked. Export result to filemaker. BANG DONE. (Localization?)
