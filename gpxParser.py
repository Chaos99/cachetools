from xml.parsers import expat

class pers():
   count = 0   
   logcount = 0
   ownlogcount = 0
   ownfoundlogcount = 0
   wordcount = 0   
   isown = False
   isfound = True
   haslog = False
   hasownlog = False
   hasownfoundlog = False
   username = ''
   stack = []
   currentCache = ''
   words = []
   typeCount ={}
   
   

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
         pers.haslog = True
         pers.logcount = pers.logcount + 1


   def end(self, name):
      if pers.stack.pop() != name:
         print "badly formated XML"
      if name == 'groundspeak:log':
         pers.isown = False
         pers.isfound = False
      if name == 'wpt':
         if not pers.haslog:
            print "Cache without log: " + str(pers.currentCache)
         if not pers.hasownlog:
            print "Cache without own log: " + str(pers.currentCache)
         if not pers.hasownfoundlog:
            print "Cache without own found log: " + str(pers.currentCache)
         else:
            pers.ownfoundlogcount = pers.ownfoundlogcount + 1;
         pers.haslog = False
         pers.hasownlog = False
         pers.hasownfoundlog = False


   def data(self, data):
      if 'groundspeak:log' not in pers.stack and pers.stack[-1]=='groundspeak:type':
         self.countType(data.strip())
      if 'groundspeak:log' in pers.stack and pers.stack[-1]=='groundspeak:type':       
         if data == 'Found it' or data == 'Attended':
            pers.isfound = True            
      if 'groundspeak:log' in pers.stack and pers.stack[-1]=='groundspeak:text':
         if pers.isown and pers.isfound:
            self.countWords(data)
            pers.hasownfoundlog = True
      if 'groundspeak:log' in pers.stack and pers.stack[-1]=='groundspeak:finder':       
         if data == pers.username:
            pers.isown = True
            pers.hasownlog = True

            pers.ownlogcount = pers.ownlogcount + 1
         else:
            print "Foreign Log from " + data + " found."
      if pers.stack[-1] == 'name':
         pers.currentCache = data
   
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
      