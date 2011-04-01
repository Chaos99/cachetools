''' GPX related classes as well as persistent data storage.'''

from xml.parsers import expat
from datetime import datetime
from collections import defaultdict
from geoTools import geoTools
from ConfigParser import SafeConfigParser as ConfigParser

def count_words(text):
    ''' Count word-like blocks of letters in logs.'''
    stripped_text = ""
    for let in text:
        if let.isalpha() or let == ' ':
            stripped_text += let
        else:
            stripped_text += ' '
    words = stripped_text.strip().split(None)
    wordcount = len(words)
    Pers.wordcount = Pers.wordcount + wordcount
    Pers.words.append(wordcount)
    return wordcount

def count_type(name):
    ''' Produce a histogram of cache types.'''
    if name in Pers.typeCount.keys():
        Pers.typeCount[name] = Pers.typeCount[name] + 1
    else:
        Pers.typeCount[name] = 1

def count_container(name):
    ''' Produce a histogram if cache containers.'''
    if name in Pers.containerCount.keys():
        Pers.containerCount[name] = Pers.containerCount[name] + 1
    else:
        Pers.containerCount[name] = 1

def count_date(date):
    ''' Produce histogram of days, months and years; possible deprecated.'''
    if date.year not in Pers.dateCount.keys():
        Pers.dateCount[date.year] = {}
    if date.month not in Pers.dateCount[date.year].keys():
        Pers.dateCount[date.year][date.month] = {}
    if date.day not in Pers.dateCount[date.year][date.month].keys():
        Pers.dateCount[date.year][date.month][date.day] = 1
    else:
        Pers.dateCount[date.year][date.month][date.day] += 1

class Pers():
    '''Persistent storage of global informations (including results)'''
    count = 0
    logcount = 0
    ownlogcount = 0
    ownfoundlogcount = 0
    wordcount = 0
    username = ''
    stack = []
    words = []
    typeCount = {}
    tenCount = 0
    containerCount = {}
    dateCount = {}
    #HCCCount = 0
    #FTFcount = 0
    LostnFoundCount = 0
    Matrix = defaultdict(lambda: defaultdict(lambda: 0))
    countryList = defaultdict(lambda: 0)
    stateList = defaultdict(lambda: defaultdict(lambda: 0))
    _allFound = [] # possibly deprecated
    home = None
    max_distance = [None, 0]

class GeoCache():
    ''' Struct like class to hold a single Geocached parsed from gpx.'''
    class Logs():
        ''' Sub-struct to hold saved logs.'''
        def __init__(self, lid):
            self.lid = lid
            self.finder = dict(uid=None, name=None)
    def __init__(self, **keys):
        self.gid = ""
        self.owner = {}
        self.attributes = {}
        self.logs = {}
        self.travelbugs = {}
        self.coords = None
        self.placed = None
        self.height = None
        self.__dict__.update(keys)

class GpxParser():
    ''' Parser for pocket query gpx files from Geocaching.com.'''
    def __init__(self, _pers):
        self.stack = []
        self.pers = _pers
        self._parser = expat.ParserCreate()
        self._parser.buffer_text = True
        self._parser.StartElementHandler = self.start
        self._parser.EndElementHandler = self.end
        self._parser.CharacterDataHandler = self.conddata
        self.isown = False
        self.isfound = False
        self.haslog = False
        self.hasownlog = False
        self.hasownfoundlog = False
        self.current_name = None
        self.logtime = None
        self.cache = ConfigParser()
        self.current_cache = None
        self.all_caches = []
        self.ignore_wpt = False
        self.current_country = None
        self.current_difficult = None
        self.current_time = None
        self.last_date = None
        self.current_terrain = None
        self.current_height = None
        self.current_coords = None

        self.cache.read('cache.dat')
        if not (self.cache.has_section('HEIGHT') and
            self.cache.has_section('STATE')):

            self.cache.add_section('HEIGHT')
            self.cache.add_section('STATE')
            with open('cache.dat', 'wb') as cachefile:
                self.cache.write(cachefile)
            print "No cache file found. A new one was generated."
            self.cache.read('cache.dat')

    def feed(self, _file, row):
        ''' Parse gpx file content.'''
        return self._parser.Parse(_file, row)
    
    def start(self, name, attrs):
        ''' Process start tags; handle stack; count wpts; count logs.'''
        self.stack.append(name)
        if name == 'wpt':
            Pers.count  += 1
            self.current_coords = (float(attrs['lat']), float(attrs['lon']))
        elif name == 'groundspeak:log':
            self.haslog = True
            Pers.logcount = Pers.logcount + 1
    
    def end(self, name):
        ''' process end tags; handle stack; finalize wpt; handle EOF.'''
        if self.stack.pop() != name:
            print "badly formated XML"
        if name == 'groundspeak:log':
            self.isown = False
            self.isfound = False
        elif name == 'wpt':
            if self.ignore_wpt:
                self.ignore_wpt = False
            else:
                if not self.haslog:
                    print("Cache without log: " +
                           str(self.current_name).encode('ascii', 'ignore'))
                if not self.hasownlog:
                    print("Cache without own log: " +
                           str(self.current_name).encode('ascii', 'ignore'))
                if not self.hasownfoundlog:
                    print("Cache without own found log: " +
                          str(self.current_name).encode('ascii', 'ignore'))
                else:
                    Pers.ownfoundlogcount = Pers.ownfoundlogcount + 1
                    self.all_caches.append(self.current_cache)
                
            self.haslog = False
            self.hasownlog = False
            self.hasownfoundlog = False
    
        elif name == 'gpx':
            with open('cache.dat', 'wb') as cachefile:
                self.cache.write(cachefile)
    
    def conddata(self, _data):
        ''' Data handler wrapper to enable ignoring of verbatim sections.'''
        if not self.ignore_wpt:
            self.data(_data)
        else:
            return
    
    def data(self, data):
        ''' Handle data, call special handlers, count and store attributes.'''
        if('wpt' in self.stack and
            self.stack[-1] not in ('time','wpt','name','groundspeak:type',
                                'groundspeak:date') and
            'groundspeak:attributes' not in self.stack):
            if ":" in self.stack[-1]:
                exec("self.current_cache.%s = data"%
                    (str(self.stack[-1]).partition(':')[2]))
            else:
                exec("self.current_cache.%s = data"%(str(self.stack[-1])))
        elif self.stack[-2:] == ['wpt','time']:
            self.current_time = data
        elif self.stack[-1] == 'groundspeak:type':
            if 'groundspeak:log' in self.stack:
                self.current_cache.logtype = data
                if 'Found it' in data or 'Attended' in data:
                    self.current_cache.date = self.logtime
            else:
                self.current_cache.type = data
        elif self.stack[-1] == 'groundspeak:date':
            self.logtime = data.strip()
                
        if self.stack[-2:] == ['wpt','name']:
            if not data.strip().startswith("GC"):
                # woah, ran into a waypoint
                self.ignore_wpt = True
                Pers.count  -= 1
                return
            self.current_name = data
            self.get_height(self.current_name, self.current_coords)
            if Pers.home:
                dist = geoTools.get_distance(Pers.home, self.current_coords)
                if dist > Pers.max_distance[1]:
                    Pers.max_distance = (data, dist)
                else:
                    Pers.max_distance = Pers.max_distance
            # internal model
            self.current_cache = GeoCache(gid = data)
            self.current_cache.coords = self.current_coords
            self.current_cache.placed = self.current_time
            self.current_cache.height = self.current_height
    
        elif(self.stack[-1]=="desc"  and "10 Years!" in data):
            Pers.LostnFoundCount += 1
        elif('groundspeak:log' not in self.stack and
            self.stack[-1] == 'groundspeak:type'):
            count_type(data.strip())
        elif('groundspeak:log' in self.stack and
            self.stack[-1] == 'groundspeak:type'):
            if data == 'Found it' or data == 'Attended':
                self.isfound = True            
        elif('groundspeak:log' in self.stack and
            self.stack[-1] == 'groundspeak:text'):
            if self.isown and self.isfound:
                count_words(data)
                self.hasownfoundlog = True
                #Pers.allFound.append(self.current_name)
                #if 'FTF' in data:
                    #Pers.FTFcount = Pers.FTFcount + 1
        elif('groundspeak:log' in self.stack and
            self.stack[-1] == 'groundspeak:finder'):
            if data == Pers.username:
                self.isown = True
                self.hasownlog = True
                Pers.ownlogcount = Pers.ownlogcount + 1
                count_date(self.last_date)
    
        elif self.stack[-1] == 'groundspeak:name':
            if '10 Years!' in data:
                Pers.tenCount = Pers.tenCount + 1
        elif self.stack[-1] == 'groundspeak:container':
            count_container(data.strip())
        elif self.stack[-1] == 'groundspeak:difficulty':
            self.current_difficult = float(data)
        elif self.stack[-1] == 'groundspeak:terrain':
            self.current_terrain = float(data)
            Pers.Matrix[self.current_difficult][self.current_terrain] += 1
            #if self.current_terrain == 5 and self.current_difficult == 5:
                #Pers.HCCCount = Pers.HCCCount + 1
        elif self.stack[-1] == 'groundspeak:date':
            try:
                self.last_date = datetime.strptime(data,'%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                self.last_date = datetime.strptime(data,'%Y-%m-%dT%H:%M:%S')
        elif self.stack[-1] == "groundspeak:country":
            #and data not in Pers.countryList:
            Pers.countryList[data.strip()] += 1
            self.current_country = data.strip()
        elif self.stack[-1] == "groundspeak:state":
            if data.strip() == "":
                data = self.get_state(self.current_name, self.current_coords)
            Pers.stateList[self.current_country][data.strip()] += 1
    
    def get_height(self, name, coords):
        ''' Ask GeoTools for height, compute min and max.'''
        if self.cache.has_option('HEIGHT', name):
            height = self.cache.getfloat('HEIGHT', name)
        else:
            height = geoTools.get_height(coords)
            self.cache.set('HEIGHT', name, str(height))
        self.current_height = height
        try:
            Pers.hMax = height if height > Pers.hMax else Pers.hMax
            Pers.hMin = height if height < Pers.hMin else Pers.hMin
        except AttributeError:
            # doing this in except instead of if/else cause this only
            # happens once
            Pers.hMax = height
            Pers.hMin = height
    
    def get_state(self, name, coords):
        ''' Get state for geocache, either from cache or by asking geotools.'''
        if self.cache.has_option('STATE', name):
            state = self.cache.get('STATE', name)
        else:
            state = geoTools.get_state(coords)
            self.cache.set('STATE', name, state)
        return state