#This file provides a function for looking up the printer friendly lcbo page online and scraping it for various fields in order to create an object of type "wineObjectClass"
#It can be used along with a CSPC list to basically create a mirror of the LCBO site.
import re
import httplib2
h=httplib2.Http('.cache')
encod="ISO-8859-1"
def cspclook(txt,):
    url = 'http://www.lcbo.com/lcbo-ear/lcbo/product/printerFriendly.do?language=EN&itemNumber='+txt
    response, content = h.request(url)
    return content
class wineObjectClass:
    def __init__(self,instream,rawcspc):
        self.encoding="ISO-8859-1"
        self.description=""
        self.inp=instream
        #I think this should work without (.*?) below, since I don't think (.*?) should ever match anything unless theres something before it to bridge two matching regions. I just noticed this after finishing and don't want to break anything so I'll leave it.
        self.datasplit=re.findall('(.*?)<br>',self.inp, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        self.cspc=rawcspc
        self.setVars(self.datasplit)
    def setVars(self,txtlist):
    # The first regular expression determines if anything about the wine can be found at all. If the text between the second set of "<br>" (datasplit[1]) tags
    # It checks that after the br tags there is a releaser (LCBO or VINTAGES) as well as a CSPC and everything after the | character (assumed to be bottle size)
        prog = re.compile('(\w*)\s*(\d+).*\|\ (.*\\b)', re.MULTILINE | re.IGNORECASE | re.DOTALL)
        # This block is just to initialize variables to "not found" defaults"
        if prog.search(txtlist[1].strip()) is None:
            self.releaser="notfound"
            self.name="notfound"
            #self.cspc="notfound"
            self.bottlesize="notfound"
            self.country="notfound"
            self.producer="notfound"
            self.save=0
            self.airmiles=0
            self.until="unknown"
            self.typesubtype="notfound"
            self.ptype="notfound"
            self.sugar=""
            self.alcohol=""
            self.VQA=0
            self.releasedate=""
            self.price=0
        # This block is where the magic happens. If a match is found, what else to do
        # with it is found here.
        else:
            self.price=444
            #NAME, RELEASER, BOTTLE SIZE, TYPESUBTYPE are completely straightforward also, always between particular tags
            #The name of wine is always between those span tags. 
            #It's not running this re on the datasplit version, it's on the instream version of the page
            prog2 = re.compile('<span class="medium-title">(.*?)</span>',)
            self.name=prog2.search(self.inp).group(1).strip()
            #The releaser and bottle size are from the datasplit regex. 
            #CSPC is in there too but unneeded
            self.releaser=prog.search(txtlist[1].strip()).group(1).strip()
            #self.cspc= prog.search(txtlist[1].strip()).group(2).strip()
            self.bottlesize=prog.search(txtlist[1].strip()).group(3).strip()
            #COUNTRY, REGION, PRODUCER are also pretty clear. fresh regexes though.
            prog3 = re.compile('Made\ in:\ (.*?)<BR>')
            self.country=prog3.search(self.inp).group(1).strip()
            prog4 = re.compile('By:(.*?)<BR>')
            self.producer=prog4.search(self.inp).group(1).strip()
            pricetemp=re.search('Price:\ \$\ (.*?)<',self.inp, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if pricetemp is None:
                self.price=""
            else:
                self.price=float(pricetemp.group(1).strip())
            #PRICE, DESCRIPTION, SERVING SUGGESTION & THE LARGE OPTIONAL FIELDS  
            #All of the "Description", "Tasting Notes", "Serving Suggestion" 
            #and other such things tend to be headed by a font change as below,
            #following up on the next line also. Price is handled as well, but differently
            prog5 = re.compile('<font color.*?><B>(\w.*?)</B></font><BR>(.*?)<BR>', re.MULTILINE | re.IGNORECASE | re.DOTALL)
            #The iterator returned by finditer allows as many matching "Description",
            #"Tasting Notes", or whatever else to both be included
            if prog5.search(self.inp) is None:
                self.description=""
            else:
                for b in prog5.finditer(self.inp):
            #again note the strange logic, if you dont match price, you match description and add to it.
            #this is because price also uses the font change, so we have to deal with it
            #seperately
                       self.description=self.description+b.group(1).strip()+"\n"+b.group(2).strip()+"\n\n"
            #SAVE: AM's code is a little cleaner but they are basically the same
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
