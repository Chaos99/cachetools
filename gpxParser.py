from xml.parsers import expat
from datetime import datetime
from collections import defaultdict
from geoTools import geoTools
from ConfigParser import SafeConfigParser as ConfigParser

class pers():
   '''Persistent storage of global informations (including results)'''
   count = 0   
   logcount = 0
   ownlogcount = 0
   ownfoundlogcount = 0
   wordcount = 0
   username = ''
   stack = []   
   words = []
   typeCount ={}
   tenCount = 0
   containerCount = {}
   dateCount = {}
   HCCCount = 0
   FTFcount = 0
   LostnFoundCount = 0
   Matrix = defaultdict(lambda: defaultdict(lambda: 0))   
   countryList = defaultdict(lambda: 0)
   stateList = defaultdict(lambda: defaultdict(lambda: 0))
   allFound = []
   home = None
   maxDistance = [None, 0]
   #completeCache= defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))

class GeoCache():
   class Logs():
      def __init__(self, lid):
         self.lid = lid
         self.finder = dict(uid=None, name=None)
   def __init__(self, gid):
      self.gid = gid
      self.owner = {}
      self.attributes = {}
      self.logs = {}
      self.travelbugs = {}

class gpxParser():
   def __init__(self, _pers):
      self.pers = _pers
      self._parser = expat.ParserCreate()
      self._parser.buffer_text = True
      self._parser.StartElementHandler = self.start
      self._parser.EndElementHandler = self.end
      self._parser.CharacterDataHandler = self.data
      self.isown = False
      self.isfound = False
      self.haslog = False
      self.hasownlog = False
      self.hasownfoundlog = False
      self.currentName = None
      self.cache = ConfigParser()
      self.currentCache = None
      
      try:
         self.cache.read('cache.dat')
         if not (self.cache.has_section('HEIGHT') and self.cache.has_section('STATE')):
            raise Exception()
                      
      except:      
         self.cache.add_section('HEIGHT')
         self.cache.add_section('STATE')
         with open('cache.dat', 'wb') as cachefile:
            self.cache.write(cachefile)
         print "No cache file found. A new one was generated."
         self.cache.read('cache.dat')
      #self.currentTime = None
      #self.start = False

   def feed(self, _file, n):
      return self._parser.Parse(_file,n)

   def start(self, name, attrs):
      pers.stack.append(name)
      if name == 'wpt':      
         #self.start = True
         pers.count  = pers.count + 1
         self.currentCoords= (float(attrs['lat']),float(attrs['lon']))
      elif name == 'groundspeak:log':
         self.haslog = True
         pers.logcount = pers.logcount + 1
      #elif self.start and len(attrs) > 0 and name != 'time':
      #   for a in attrs:
      #      pers.completeCache[self.currentName][name][a] = attrs[a]


   def end(self, name):
      if pers.stack.pop() != name:
         print "badly formated XML"
      if name == 'groundspeak:log':
         self.isown = False
         self.isfound = False
      elif name == 'wpt':
         if not self.haslog:
            print "Cache without log: " + str(self.currentName)
         if not self.hasownlog:
            print "Cache without own log: " + str(self.currentName)
         if not self.hasownfoundlog:
            print "Cache without own found log: " + str(self.currentName)
         else:
            pers.ownfoundlogcount = pers.ownfoundlogcount + 1;
         self.haslog = False
         self.hasownlog = False
         self.hasownfoundlog = False
      elif name == 'gpx':
         with open('cache.dat', 'wb') as cachefile:
            self.cache.write(cachefile)


   def data(self, data):
      if 'wpt' in pers.stack and pers.stack[-1] not in ('time','wpt','name','groundspeak:type') and 'groundspeak:attributes' not in pers.stack:
         if ":" in pers.stack[-1]:
            exec("self.currentCache.%s = data"%(str(pers.stack[-1]).partition(':')[2]))
         else:
            exec("self.currentCache.%s = data"%(str(pers.stack[-1])))
      elif 'wpt' in pers.stack and pers.stack[-1] == 'time':
         self.currentTime = data         
      elif pers.stack[-1] == 'groundspeak:type':
         if 'groundspeak:log' in pers.stack:
            self.currentCache.logtype = data
         else:
            self.currentCache.type = data
      
         
      if pers.stack[-1] == 'name' and 'wpt' in pers.stack:
         self.currentName = data
         self.getHeight(self.currentName, self.currentCoords)
         dist = geoTools.getDistance(pers.home, self.currentCoords)
         pers.maxDistance = (data, dist) if dist > pers.maxDistance[1] else pers.maxDistance
         # internal model
         self.currentCache = GeoCache(data)
         self.currentCache.coords = self.currentCoords
         self.currentCache.placed = self.currentTime
         self.currentCache.height = self.currentHeight
         
         
      #elif pers.stack[-1] == 'time':
      #   self.currentTime = data
      elif pers.stack[-1]=="desc" and "10 Years!" in data:
         pers.LostnFoundCount +=1
      elif 'groundspeak:log' not in pers.stack and pers.stack[-1]=='groundspeak:type':
         self.countType(data.strip())
      elif 'groundspeak:log' in pers.stack and pers.stack[-1]=='groundspeak:type':       
         if data == 'Found it' or data == 'Attended':
            self.isfound = True            
      elif 'groundspeak:log' in pers.stack and pers.stack[-1]=='groundspeak:text':
         if self.isown and self.isfound:
            self.countWords(data)
            self.hasownfoundlog = True
            pers.allFound.append(self.currentName)
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
      elif pers.stack[-1]=='groundspeak:name':
         if '10 Years!' in data:
            pers.tenCount = pers.tenCount + 1
      elif pers.stack[-1]=='groundspeak:container':
         self.countContainer(data.strip())
      elif pers.stack[-1]=='groundspeak:difficulty':
         self.currentDifficult = float(data)
      elif pers.stack[-1]=='groundspeak:terrain':
         self.currentTerrain = float(data)
         pers.Matrix[self.currentDifficult][self.currentTerrain] +=1
         if self.currentTerrain == 5 and self.currentDifficult == 5:
            pers.HCCCount = pers.HCCCount + 1
      elif pers.stack[-1]=='groundspeak:date':    
         try:     
            self.lastDate = datetime.strptime(data,'%Y-%m-%dT%H:%M:%SZ')
         except:
            self.lastDate = datetime.strptime(data,'%Y-%m-%dT%H:%M:%S')      
      elif pers.stack[-1] == "groundspeak:country": #and data not in pers.countryList:
         pers.countryList[data.strip()] += 1
         self.currentCountry = data.strip()
      elif pers.stack[-1] == "groundspeak:state":
         if data.strip() == "":
            data = self.getState(self.currentName, self.currentCoords)
            #pers.completeCache[self.currentName]["groundspeak:state"]['data'] = data.strip()
         pers.stateList[self.currentCountry][data.strip()] += 1
         
   
   def countWords(self, _text):
      strippedText = ""
      for t in _text:
         if t.isalpha() or t==' ':
            strippedText += t
         else:
            strippedText += ' '
      words = strippedText.strip().split(None)
      wordcount = len(words)
      pers.wordcount = pers.wordcount + wordcount  
      pers.words.append(wordcount)
      return wordcount
   
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
         
   def getHeight(self, name, coords):
      if self.cache.has_option('HEIGHT', name):
         h = self.cache.getfloat('HEIGHT', name)
      else:
         h = geoTools.getHeight(coords)
         self.cache.set('HEIGHT',name,str(h))
      self.currentHeight = h
      try:
         pers.hMax = h if h > pers.hMax else pers.hMax
         pers.hMin = h if h < pers.hMin else pers.hMin
      except:
         # doing thin in except instead of if/else cause this only happens once
         pers.hMax = h
         pers.hMin = h

   def getState(self, name, coords):
      if self.cache.has_option('STATE', name):
         s = self.cache.get('STATE', name)
      else:
         s = geoTools.getState(coords)
         self.cache.set('STATE',name,s)
      return s