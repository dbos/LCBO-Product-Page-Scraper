################################################################################
#Author: Danny O'Sullivan
#
#Dependancies: httplib2
#
#Description: This file provides a function for looking up the printer friendly 
#lcbo page online and scraping it for various fields in order to create an 
#object of type "wineObjectClass" It can be used along with a CSPC list to 
#basically create a mirror of the LCBO site, or look up products on demand.
#
#Usage: It's intended to be used as a library. One could import it, and then
# do something like:
#	x=wineObject.wineObjectClass(216)
#       print str(x.cspc)+" has product name: "+str(x.name)
#
#TODO:
#	Clean up encoding mess
#	Better failed lookups than returning fields filled with "unknown"
#	Remove unused variables from older versions (e.g. psubtype, region)
#	Some fields (such as "until") run on beyond the data they are
#		intended for. Make regex more precise
#	Make it figure out if discount has already been applied to LTOs
#
#Other Notes:
#	This library could become obsolete at any time. If it can be maintained
#	by simply updating the regular expressions in this file, that would be
#	great. Besides finding the descrition data, most of this is just simple
#	regular expressions applied to raw html provided by httplib2
#
################################################################################
import re
import httplib2
h=httplib2.Http('.cache')
encoding="iso-8859-1"
def cspclook(txt,):
    url = 'http://www.lcbo.com/lcbo-ear/lcbo/product/printerFriendly.do?language=EN&itemNumber='+txt
    response, content = h.request(url)
    return content
class wineObjectClass:
    def __init__(self,instream,rawcspc):
	self.description=""
        self.inp=unicode(instream.decode(encoding))
        #The point of datasplit is to break the html up into segments divided by <br> tags. 
	#Between the appropriately numbered <br> tag lies useful data, as the regex's below all use
	self.datasplit=re.findall('(.*?)<br>',self.inp, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        self.cspc=rawcspc
        self.setVars(self.datasplit)
    def setVars(self,txtlist):
    # This first regular expression determines if anything about the wine can be found at all. 
    # If the text between the second set of "<br>" (datasplit[1]) tags exists it goes on
    # This is where proper error checking should be employed instead of these lame "notfound" defaults.
        prog = re.compile('(\w*)\s*(\d+).*\|\ (.*\\b)', re.MULTILINE | re.IGNORECASE | re.DOTALL)
    # It checks that after the br tags there is a releaser (LCBO or VINTAGES) as well as a CSPC 
    # and for text after the | character (which is bottle size) note that this is just how the 
    # releaser is formatted. Like the other regex's it depends on how the LCBO lists products.
        if prog.search(txtlist[1].strip()) is None:
            self.releaser=""
            self.name=""
            #self.cspc="notfound"
            self.bottlesize=""
            self.country=""
            self.producer=""
            self.save=0
            self.airmiles=0
            self.until=""
            self.typesubtype=""
            self.ptype=""
            self.sugar=""
            self.alcohol=""
            self.VQA=0
            self.releasedate=""
            self.price=0
        # This block is where the magic happens. If a match is found, what else to do
        # with it is found here.
        else:
            #NAME, RELEASER, BOTTLE SIZE, TYPESUBTYPE are straightforward, between particular tags
            #The name of wine is always between those span tags which only appear once, hence it's
            #not running this re on the datasplit version, it's on the instream version of the page
            prog2 = re.compile('<span class="medium-title">(.*?)</span>',)
            self.name=prog2.search(self.inp).group(1).strip()

            #The releaser and bottle size are from datasplit, in their respective <br> blocks.
            #(CSPC is in there too but unneeded, since it's the argument to the class constructor)
            self.releaser=prog.search(txtlist[1].strip()).group(1).strip()
            #self.cspc= prog.search(txtlist[1].strip()).group(2).strip()
            self.bottlesize=prog.search(txtlist[1].strip()).group(3).strip()

            #COUNTRY, REGION, PRODUCER are also pretty clear. fresh regexes though.
            prog3 = re.compile('Made\ in:\ (.*?)<BR>')
            self.country=prog3.search(self.inp).group(1).strip()
            prog4 = re.compile('By:(.*?)<BR>')
            self.producer=prog4.search(self.inp).group(1).strip()
            
	    
	    #OK it gets pretty hairy here. See comments below. 
	    pricetemp=re.search('Price:\ \$\ (.*?)<',self.inp, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if pricetemp is None:
                self.price=""
            else:
                self.price=float(pricetemp.group(1).strip())
            
	    #PRICE, DESCRIPTION, SERVING SUGGESTION & THE LARGE OPTIONAL FIELDS  
	    #
            #All of the "Description", "Tasting Notes", "Serving Suggestion" 
            #and other such things tend to be headed by a font change as below,
            #following up on the next line also. Price confounds this by also
	    #using the font change. 
            prog5 = re.compile('<font color.*?><B>(\w.*?)</B></font><BR>(.*?)<BR>', re.MULTILINE | re.IGNORECASE | re.DOTALL)
            #The iterator returned by finditer allows as many matching "Description",
            #"Tasting Notes", or whatever else to both be included
            if prog5.search(self.inp) is None:
                self.description=""
            else:
                for b in prog5.finditer(self.inp):
			#have to iterate all of the matches, in case more than one description
			#exists, for example some wines have both a "Description" and a
			#"Serving Suggestion". I add all of these together; iterate and concat
                       self.description=self.description+b.group(1).strip()+"\n"+b.group(2).strip()+"\n\n"

            #SAVE: AM's code is a little cleaner but they are basically doing the exact same thing
            savings=re.compile('Save:.*\$\ ([\d\.]*)', re.MULTILINE | re.DOTALL) 
            if savings.search(self.inp) is None:
                self.save=0
                self.until="unknown"
            else:
                self.save=float(savings.search(self.inp).group(1).strip())
		self.price+=self.save
                finduntil=re.compile('Until\s*\n\s*(.*?)\n', re.MULTILINE | re.DOTALL) 
                if finduntil.search(self.inp) is None:
                    self.until="unknown"
                else:
                    self.until=finduntil.search(self.inp).group(1).strip()
            #AM
            airmiles= re.compile('Earn[\s\n]*?([\d\.]*)[\s\n]*?AIR[\s\n]*?MILES.*?Until[\s\n]*(.*?)\n', re.MULTILINE | re.DOTALL)
            if airmiles.search(self.inp) is None:
                self.airmiles=0
            else:
                self.airmiles=airmiles.search(self.inp).group(1).strip()
                self.until=airmiles.search(self.inp).group(2).strip()

            #TYPESUBTYPE
                 #This is a huge PITA. The block that has the type and subtype
                 #follows either PRICE, LTO, AM, or Both in front, and
                 #nothing remotely consistent after. Once the block is found,
                 #all that needs to be done is to strip the block and split
                 #those two. 

		 #UPDATE:  Note that 3 fields were once involved in gathering
		 #country/region and type/subtype combos, I was splitting the
		 #"Wine,Red Wine" on the comma into two new fields, and doing
		 #the same for country/region. Now I just keep it as is so 
		 #there is some serious code cleanup to do.

            prog6=re.compile('\s\s([^\n]*?)<br>\s*([%\d\.]*)\ Alcohol/Vol.<br>', re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if prog6.search(self.inp) is None:
                self.typesubtype="notfound,notfound"
                self.ptype="notfound"
            else:
                self.typesubtype=prog6.search(self.inp).group(1).strip()
                self.abv=prog6.search(self.inp).group(2).strip()
            #TYPE, SUBTYPE, ABV
                typesubtypere=re.compile("(.*),(.*)")
                if typesubtypere.search(self.typesubtype) is None:
                    self.typesubtype=","
                    self.ptype=""
                else:
                    self.ptype = typesubtypere.search(self.typesubtype).group(1)+","+typesubtypere.search(self.typesubtype).group(2).strip()
            #VQA
            prog7=re.compile('<b>VQA</b>', re.IGNORECASE)
            if prog7.search(self.inp) is None:
                self.VQA = 0
            else:
                self.VQA = 1
            #RSugar
            prog8=re.compile('Sugar\ Content\ :\ (.*?)<br>', re.IGNORECASE)
            if prog8.search(self.inp) is None:
                self.sugar=""
            else:
                self.sugar=prog8.search(self.inp).group(1).strip()
            prog9=re.compile('Release\ Date:[\ \t\n]*(.*)<br>', re.MULTILINE | re.IGNORECASE | re.DOTALL)
            if prog9.search(self.inp) is None:
                self.releasedate="unknown2"
            else:
                self.releasedate=prog9.search(self.inp).group(1).strip()
            prog10=re.compile('[\ \t\n\r](.*?)\%\ Alcohol', re.IGNORECASE)
            if prog10.search(self.inp) is None:
                self.alcohol=""
            else:
                self.alcohol=prog10.search(self.inp).group(1).strip()
