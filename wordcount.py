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
   isown = False
   isfound = True
   username = ''
   stack = []
   


# 3 handler functions
def start_element(name, attrs):
   pers.stack.append(name)
   if name == 'wpt':      
      pers.count  = pers.count + 1
   if name == 'groundspeak:log':
      pers.logcount = pers.logcount + 1   


def end_element(name):
   if pers.stack.pop() != name:
      print "badly formated XML"
   if name == 'groundspeak:log':
      pers.isown = False
      pers.isfound = False


def char_data(data):
    if 'groundspeak:type' in pers.stack:       
       if data == 'Found it' or data == 'Attended':
         pers.isfound = True
         pers.ownfoundlogcount = pers.ownfoundlogcount + 1;
    if 'groundspeak:log' in pers.stack and pers.stack[-1]=='groundspeak:text':
       if pers.isown and pers.isfound:
         countWords(data)
    if 'groundspeak:log' in pers.stack and pers.stack[-1]=='groundspeak:finder':       
       if data == pers.username:
          pers.isown = True
          pers.ownlogcount = pers.ownlogcount + 1

def countWords(_text):   
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