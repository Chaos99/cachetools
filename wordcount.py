#!python
# -*- coding: UTF-8 -*-

from xml.parsers import expat
from HTMLParser import HTMLParser
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
   

class badge():
   
   user = "TheSearchers"   
   userIsMult = False
   path = "./"   
   levels = ['B','S','G','P','R','Sa', 'E', 'D']
   num = 10
   goal = 90
   
   def __init__(self, _name, _desc='awarded for programming batch classes', _verbs='has done', _verbm='have done', _icon='Trad'):
      self.name  = _name
      self.desc = _desc
      self.verbs = _verbs
      self.verbm = _verbm 
      self.icon = _icon
      self.goals = []
   
   @classmethod
   def setUser(_class, _user,_m):
      _class.user= _user      
      _class.userIsMult = _m
     
   @classmethod
   def setPath(_class, _path):
      _class.path= _path
   
   def setLevels(self, _goals):
      if len(_goals) == 8:
         self.goals= _goals
      else:
         print "Not a valid list of level goals"
   
   def setStatus(self, _num):
      self.num = _num
      #if self.goals.isempty() :
      self.level = None
      for g,l in zip(self.goals, self.levels):
         if _num >= g:
            self.level = l
            self.goal = self.goals[self.goals.index(g)+1] if l != 'D' else 0
         else:
            pass
   
   def overridePath(self, _path):
      self.path= _path
  
   def getHTML(self):
      verb = self.verbm if self.userIsMult else self.verbs
      if self.level == 'D':
         alt = "%s, %s | %s %s %d, %s reached the highest level>"%(self.name, self.desc, self.user, verb, self.num, 'have' if self.userIsMult else 'has')
         return '<img src="%s%s%s.png" \n\talt  = "%s" \n\ttitle= "%s"\n/>'%(self.path, self.icon, self.level, alt, alt)
      if self.level != None:
         alt = "%s, %s | %s %s %d, %s %d (+%d) for next level>"%(self.name, self.desc, self.user, verb, self.num, 'need' if self.userIsMult else 'needs', self.goal, self.goal-self.num)
         return '<img src="%s%s%s.png" \n\talt  = "%s" \n\ttitle= "%s"\n/>'%(self.path, self.icon, self.level, alt, alt)
      else:
         return '<! No %s generated. %s %s only %d. %s %d (+%d) for level 1.>'%(self.name, self.user, verb, self.num, 'Need' if self.userIsMult else 'Needs', self.goals[0], self.goals[0]-self.num)
   

class gpxParser():
# 3 handler functions
   def __init__(self, _pers):
      self.pers = _pers
      self._parser = expat.ParserCreate()
      self._parser.buffer_text = True
      self._parser.StartElementHandler = self.start
      self._parser.EndElementHandler = self.end
      self._parser.CharacterDataHandler = self.data

   def feed(self, _file, n):
      return self._parser.Parse(_file,n)

   def start(self, name, attrs):
      pers.stack.append(name)
      if name == 'wpt':      
         pers.count  = pers.count + 1
      if name == 'groundspeak:log':
         pers.logcount = pers.logcount + 1   

   def end(self, name):
      if pers.stack.pop() != name:
         print "badly formated XML"
      if name == 'groundspeak:log':
         pers.isown = False
         pers.isfound = False

   def data(self, data):
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

class htmlParser(HTMLParser):

   def __init__(self):
      HTMLParser.__init__(self)
      self.stack=[]
      self.entity = None
      self.nameSig = ['html', 'body', 'table', 'tr', 'td', 'table', 'tr', 'td', 'table', 'tbody', 'tr', 'td', 'b']
      self.descSig = ['html', 'body', 'table', 'tr', 'td', 'table', 'tr', 'td', 'table', 'tbody', 'tr', 'td']
      self.iconSig = ['html', 'body', 'table', 'tr', 'td', 'table', 'tr', 'td', 'table', 'tbody', 'tr', 'td']
      self.names=[]
      self.descs=[]
      self.icons=[]
      self.paths=[]    
   
   def handle_charref(self, name):
      print 'charref ' + name   

   def handle_entityref(self, name):      
      self.entity = self.unescape('&'+name+';')

   def handle_starttag(self, name, attrs):
      self.stack.append(name)
      if self.iconSig == self.stack[:-1] and name == 'img' and len(self.icons)+1 == len(self.names):
         src = attrs[2][1]
         path,x,icon = src.rpartition('/')         
         self.icons.append(icon[:-5])
         self.paths.append(path+'/')
         #print path
         #print icon[:-5]        
      #print str(self.stack)
      
   def handle_endtag(self, name):
      self.entity = None
      if name == 'html':
         self.finish()
      while self.stack.pop() != name:
         pass         

   def handle_data(self, data):
      if self.nameSig == self.stack:
         if self.entity:
            self.names.append(self.names.pop() + self.entity + data)
            self. entity = None
         else:
            self.names.append(data)
         
      if self.descSig == self.stack:
         if self.entity and self.stack != []:
            self.descs.append(self.descs.pop() + self.entity + data)
         elif data.strip(' ()').startswith('award'):
            self.descs.append(data)

   def finish(self):
      self.names = [a.strip() for a in self.names]
      self.descs = [a.strip(' ()') for a in self.descs]
           
         
      #if 'Traditional' in data:
      #   print str(self.stack)      


def countWords(_text):   
   words = _text.split(None)
   wordcount = len(words)
   pers.wordcount = pers.wordcount + wordcount

pers.username = sys.argv[2]

p = gpxParser(pers)
h = htmlParser()

f = open(sys.argv[1],'r')
p.feed(f.read(), 1)
f.close()

f = open(sys.argv[3],'r')
h.feed(f.read())
h.close()
f.close()

print "All: "+str(pers.count)+"  With logs: "+str(pers.logcount)+"  with own logs: "+str(pers.ownlogcount)+"  thereof found: "+str(pers.ownfoundlogcount)
print "Average  word count: " + str(pers.wordcount / pers.ownfoundlogcount)

badge.setUser(pers.username, True)
badge.setPath('./')

bb = badge('Traditional Badge', 'awarded for finding traditional caches','has found','have found','Trad') 
bb.setLevels([25,50,75,100,150,200,500,1000])
bb.setStatus(235)
print bb.getHTML()