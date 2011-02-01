#!python
# -*- coding: UTF-8 -*-

import xml.parsers.expat
import sys

class pers():
   count = 0
   logcount = 0
   ownlogcount = 0
   ownfoundlogcount = 0
   wordcount = 0
   inlogs = False
   isown = False
   isfound = True
   inlogtype = False
   inownfoundlogtext = False

# 3 handler functions
def start_element(name, attrs):
   if name == 'wpt':
      pers.count  = pers.count + 1
   if name == 'groundspeak:log':
      #print 'Start element:', name, attrs
      pers.inlogs = True
      pers.logcount = pers.logcount + 1   
   if name == 'groundspeak:finder' and pers.inlogs and attrs['id']=='1902380':
      pers.isown = True
      pers.ownlogcount = pers.ownlogcount + 1
   if name == 'groundspeak:type' and pers.inlogs:
      pers.inlogtype = True   
   if name == 'groundspeak:text' and pers.inlogs and pers.isown and pers.isfound:      
      pers.inownfoundlogtext = True
      
   
      #print count
      
def end_element(name):
   if name == 'groundspeak:log':
      #print 'End element:', name
      pers.inlogs = False
      pers.isown = False
      pers.isfound = False
   if name == 'groundspeak:type' and pers.inlogs:
      pers.inlogtype = False      
   if name == 'groundspeak:text':
      pers.inownfoundlogtext = False
    
def char_data(data):
    if pers.inlogtype:       
       if data == 'Found it' or data == 'Attended':
         pers.isfound = True
         pers.ownfoundlogcount = pers.ownfoundlogcount + 1;
    if pers.inownfoundlogtext:       
       countWords(data)

def countWords(_text):
   print 'Count'
   words = _text.split(None)
   wordcount = len(words)
   pers.wordcount = pers.wordcount + wordcount



p = xml.parsers.expat.ParserCreate()

p.StartElementHandler = start_element
p.EndElementHandler = end_element
p.CharacterDataHandler = char_data


f = open(sys.argv[1],'r')

p.Parse(f.read(), 1)
f.close()

print "All: "+str(pers.count)+"  With logs: "+str(pers.logcount)+"  with own logs: "+str(pers.ownlogcount)+"  thereof found: "+str(pers.ownfoundlogcount)
print "Average  word count: " + str(pers.wordcount / pers.ownfoundlogcount)