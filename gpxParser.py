from xml.parsers import expat
from datetime import datetime
class pers():
   count = 0   
   logcount = 0
   ownlogcount = 0
   ownfoundlogcount = 0
   wordcount = 0   
   #isown = False
   #isfound = True
   #haslog = False
   #hasownlog = False
   #hasownfoundlog = False
   username = ''
   stack = []
   #currentCache = ''
   words = []
   typeCount ={}
   tenCount = 0
   containerCount = {}
   dateCount = {}
   HCCCount = 0
   FTFcount = 0
   
   

class gpxParser():
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
         self.haslog = True
         pers.logcount = pers.logcount + 1


   def end(self, name):
      if pers.stack.pop() != name:
         print "badly formated XML"
      if name == 'groundspeak:log':
         self.isown = False
         self.isfound = False
      if name == 'wpt':
         if not self.haslog:
            print "Cache without log: " + str(self.currentCache)
         if not self.hasownlog:
            print "Cache without own log: " + str(self.currentCache)
         if not self.hasownfoundlog:
            print "Cache without own found log: " + str(self.currentCache)
         else:
            pers.ownfoundlogcount = pers.ownfoundlogcount + 1;
         self.haslog = False
         self.hasownlog = False
         self.hasownfoundlog = False


   def data(self, data):
      if 'groundspeak:log' not in pers.stack and pers.stack[-1]=='groundspeak:type':
         self.countType(data.strip())
      elif 'groundspeak:log' in pers.stack and pers.stack[-1]=='groundspeak:type':       
         if data == 'Found it' or data == 'Attended':
            self.isfound = True            
      elif 'groundspeak:log' in pers.stack and pers.stack[-1]=='groundspeak:text':
         if self.isown and self.isfound:
            self.countWords(data)
            self.hasownfoundlog = True
            if 'FTF' in data:
               pers.FTFcount = pers.FTFcount + 1 
      elif 'groundspeak:log' in pers.stack and pers.stack[-1]=='groundspeak:finder':       
         if data == pers.username:
            self.isown = True
            self.hasownlog = True
            pers.ownlogcount = pers.ownlogcount + 1
            self.countDate(self.lastDate)
         else:
            print "Foreign Log from " + data + " found."
      elif pers.stack[-1] == 'name':
         self.currentCache = data
      elif pers.stack[-1]=='groundspeak:name':
         if '10 Years!' in data:
            pers.tenCount = pers.tenCount + 1
      elif pers.stack[-1]=='groundspeak:container':
         self.countContainer(data.strip())
      elif pers.stack[-1]=='groundspeak:difficulty':
         self.currentDifficult = float(data)
      elif pers.stack[-1]=='groundspeak:terrain':
         self.currentTerrain = float(data)
         if self.currentTerrain == 5 and self.currentDifficult == 5:
            pers.HCCCount = pers.HCCCount + 1
      elif pers.stack[-1]=='groundspeak:date':         
         self.lastDate = datetime.strptime(data,'%Y-%m-%dT%H:%M:%SZ')
         
   
   def countWords(self, _text):   
      words = _text.split(None)
      wordcount = len(words)
      pers.wordcount = pers.wordcount + wordcount  
      pers.words.append(wordcount)
   
   def countType(self, name):
      if name in pers.typeCount.keys():
         pers.typeCount[name]=pers.typeCount[name] + 1
      else:
         pers.typeCount[name]=1
   
   def countContainer(self, name):
      if name in pers.containerCount.keys():
         pers.containerCount[name]=pers.containerCount[name] + 1
      else:
         pers.containerCount[name]=1
         
   def countDate(self, date):      
      if date.year not in pers.dateCount.keys():
         pers.dateCount[date.year]={}
      if date.month not in pers.dateCount[date.year].keys():
         pers.dateCount[date.year][date.month]={}
      if date.day not in pers.dateCount[date.year][date.month].keys():
         pers.dateCount[date.year][date.month][date.day] = 1
      else:
         pers.dateCount[date.year][date.month][date.day] += 1
      