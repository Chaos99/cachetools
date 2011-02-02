#!python
# -*- coding: UTF-8 -*-

import xml.parsers.expat
import sys
from xml.sax.saxutils import escape


class pers():
   count = 0   
   logcount = 0
   ownlogcount = 0
   ownfoundlogcount = 0
   wordcount = 0
   inlogs = False
   inlogtype = False
   inlogfinder = False
   isown = False
   isfound = True   
   inownfoundlogtext = False
   username = ''
   stack = []
   


# 3 handler functions
def start_element(name, attrs):
   pers.stack.append(name)
   if name == 'wpt':      
      pers.count  = pers.count + 1
   if name == 'groundspeak:log':
      #print 'Start element:', name, attrs
      pers.inlogs = True
      pers.logcount = pers.logcount + 1   
   if name == 'groundspeak:finder' and pers.inlogs:
      pers.inlogfinder = True      
   if name == 'groundspeak:type' and pers.inlogs:
      pers.inlogtype = True   
   if name == 'groundspeak:text' and pers.inlogs and pers.isown and pers.isfound:      
      pers.inownfoundlogtext = True
      
   
      #print count
      
def end_element(name):
   if pers.stack.pop() != name:
      print "badly formated XML"
   if name == 'groundspeak:log':
      #print 'End element:', name
      pers.inlogs = False
      pers.isown = False
      pers.isfound = False
   if name == 'groundspeak:type' and pers.inlogs:
      pers.inlogtype = False      
   if name == 'groundspeak:text':
      pers.inownfoundlogtext = False
   if name == 'groundspeak:finder':
      pers.inlogfinder = False
    
def char_data(data):
    if pers.inlogtype:       
       if data == 'Found it' or data == 'Attended':
         pers.isfound = True
         pers.ownfoundlogcount = pers.ownfoundlogcount + 1;
    if pers.inownfoundlogtext:       
       countWords(data)
    if pers.inlogfinder:       
       if data == pers.username:
          pers.isown = True
          pers.ownlogcount = pers.ownlogcount + 1

def countWords(_text):
   print 'Count'
   words = _text.split(None)
   wordcount = len(words)
   pers.wordcount = pers.wordcount + wordcount



p = xml.parsers.expat.ParserCreate()
p.buffer_text = True

p.StartElementHandler = start_element
p.EndElementHandler = end_element
p.CharacterDataHandler = char_data

pers.username = sys.argv[2]

f = open(sys.argv[1],'r')
p.Parse(f.read(), 1)
f.close()


print "All: "+str(pers.count)+"  With logs: "+str(pers.logcount)+"  with own logs: "+str(pers.ownlogcount)+"  thereof found: "+str(pers.ownfoundlogcount)
print "Average  word count: " + str(pers.wordcount / pers.ownfoundlogcount)