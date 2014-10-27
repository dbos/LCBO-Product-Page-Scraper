################################################################################
#Author: Danny O'Sullivan
#
#Dependancies: httplib2
#
#Description: This file provides a function for looking up the lcbo page online 
#and scraping it for various fields in order to create an object with useful 
#properties. It can be used along with a CSPC list to gather all data from the
#LCBO website, or look up products on demand.
#
#Usage: It's intended to be used as a library. One could import it, and then
# do something like:
#	x=wineByCspc(216)
#       print str(x.cspc)+" has product name: "+str(x.name)
#
#Other Notes:
#	This library could become obsolete at any time; it relies on consistently
#	structured responses from http to the lcbo website. It has been updated
#	to work with the July 2014 redesign
#
################################################################################
import re
import httplib2
from bs4 import BeautifulSoup
h=httplib2.Http('/tmp/.cache')
h.follow_redirects=False
class wineObjectClass:
    def __init__(self,cspc):
        url = 'http://www.lcbo.com/lcbo/product/cspc/'+cspc
        response, content = h.request(url)
        soup=BeautifulSoup(content.decode('utf8')).find('div',class_='main-content')
        image=soup.find('div',class_='images').find('img')
        if not soup: 
            self.fail=True
            return None
        else:
            self.fail=False
        def getTagContents(query):
            try:
                return soup.find(query).string.strip()
            except:
                return ''
        def getNextSiblingContents(query):
            try:
                return soup.find('dt',text=re.compile(query)).find_next_sibling('dd').string
            except:
                return ''
        self.name=getTagContents('h1')
        self.cspc=cspc
        try:
            self.price=soup.find('div',class_='prices').strong.text
        except: 
            self.price=''
        try:
            self.ptype=','.join([tag.parent.text.strip().strip('>') for tag in soup.find_all('span',class_='breadcrumb-separator')][1:])
        except:
            self.ptype=''
        self.sugar=getNextSiblingContents('Sugar Content:')
        self.madeIn=getNextSiblingContents('Made in:')
        self.by=getNextSiblingContents('By:')
        self.sweetness=getNextSiblingContents('Sweetness Descriptor:')
        self.style=getNextSiblingContents('Style:')
        self.save=0
        self.airmiles=0
        self.until=""
        self.VQA='VQA' if soup.find(text=re.compile('This is a VQA wine')) else ''
        self.description=getTagContents('blockquote')
        self.alcohol=getNextSiblingContents('Alcohol/Vol')
        h2=httplib2.Http('/tmp/.cache')
        h2.follow_redirects=False
        response2, content2 = h.request("http://www.lcbo.com/"+image.get('src'))
        if response2.status == 200:
            self.image="http://www.lcbo.com/"+image.get('src')
        elif response2.status == 302:
            self.image="http://www.lcbo.com/"+response2['location']
