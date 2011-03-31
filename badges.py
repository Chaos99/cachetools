from cgi import escape

class badgeManager():
    ''' Class to hold all badges and their status. '''
    badges = []
    user = ""
    isMultiple=True
    stateBadgeTemplate = None
    countryList = {}
   
    @classmethod
    def populate(cls, h):
        ''' Init badges with results of a BadgeParser run.'''
        if cls.user != '':
            badge.setUser(cls.user,cls.isMultiple)
        else:
            print 'must set user before populating badge list'
        for (n,d,i,p,l) in zip(h.names,h.descs,h.icons,h.paths,h.limits):
            ba = badge(n,d, _icon=i)
            ba.overridePath(p)
            ba.setLevels(l)
            if n == "State Badges":
                cls.stateBadgeTemplate = ba
            else:
                cls.badges.append(ba)
         
    @classmethod
    def addBadge(cls, _badge):
        ''' Add a badge instance to the managed list.'''
        cls.badges.append(_badge)
   
    @classmethod
    def setStatus(cls, name, value):
        ''' Set the current status value for a badge by name.'''
        a = cls.getBadge(name)
        a.setStatus(value)
        return a.getHTML()
   
    @classmethod
    def getHTML(cls, name='ALL'):
        ''' Retrieve the HTML description of a badge; Accepts "ALL".'''
        ret = []
        for a in cls.badges:
            if name.lower() in a.name.lower() or name.lower()=='all':
                ret.append(a.getHTML())      
        return ret
   
    @classmethod
    def setCredentials(cls, user, isMultiple=True):
        ''' Set username and -count; to be set before population.'''
        cls.user = user
        cls.isMultiple = isMultiple
   
    @classmethod
    def getBadge(cls, name):
        ''' Get a badge instance by name or description.'''
        #horrible hack to solve event issue
        if name == 'event':
            name='social' 
        candidates = []
        for a in cls.badges:
            if name.lower() in a.name.lower():
                candidates.append(a)
            #no match in names? try in descriptions      
            elif name.lower() in a.desc.lower():
                candidates.append(a)
        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) > 1:
            return reduce(lambda x,y: x
                          if len(x.name) < len(y.name)
                          else y, candidates)
        else: 
            errtext = ("Sorry, no match for badge name %s\n in badges: %s"%
                        (name, str([a.name for a in cls.badges])))
            raise NameError(errtext)

    @classmethod
    def setCountryList(cls, clist):
        ''' Sets the list to be used for state badge level computation.'''
        cdict = dict()
        for line in clist.split('\n'):
            name = line.partition(',')[0].strip()
            value = int(line.partition(',')[2].strip())
            cdict[name] = value
        cls.countryList = cdict

class badge():
    ''' A single badge to be hold by the badgeManager.'''
   
    user = "TheSearchers"   
    userIsMult = False
    path = "./"   
    levels = ['B','S','G','P','R','Sa', 'E', 'D']
    num = 10
    goal = 90
   
    def __init__(self, _name, _desc='awarded for programming batch classes',
                 _verbs='has done', _verbm='have done', _icon='Trad'):
        ''' Init with name and optional description, verb and icon base name.'''
        self.name  = _name
        self.desc = _desc
        self.verbs = _verbs
        self.verbm = _verbm 
        self.icon = _icon
        self.goals = []
        self.num=None

   
    @classmethod
    def setUser(_class, _user,_m):
        ''' Set username and -count to be used in HTML output for all badges.'''
        _class.user= _user      
        _class.userIsMult = _m
     
    @classmethod
    def setPath(_class, _path):
        ''' Set the icon path for all badges.'''
        _class.path= _path
   
    def setLevels(self, _goals):
        ''' Set the requirement levels for this badge. Accepts 8 or 3 values.'''
        #print "Set levels: "+ str(_goals)
        if len(_goals) == 8:
            self.goals= [int(g) for g in _goals]         
        elif len(_goals) == 3:
            levels = ['B','P','D']
            self.goals= [int(g) for g in _goals]
        else:
            print "Not a valid list of level goals" + str(_goals)
            raise

   
    def setStatus(self, num):
        ''' Set the current status value, compute the badge level.'''
        self.num = num
        self.level = None
        if self.goals[1] >= self.goals[0]:
            # increasing goals
            for goal,level in zip(self.goals, self.levels):
                if num >= goal:
                    self.level = level
                    if level != 'D':
                        next_goal = self.goals[self.goals.index(goal)+1]
                        self.goal = next_goal
                    else:
                        self.goal = 0
        else:
            # decreasing goal
            for goal,level in zip(self.goals, self.levels):
                if num <= goal:
                    self.level = level
                    if level != 'D':
                        next_goal = self.goals[self.goals.index(goal)+1]
                        self.goal = next_goal
                    else:
                        self.goal = 0
   
    def overridePath(self, _path):
        ''' Set the icon path for this bdge, if different from class default.'''
        self.path= _path
  
    def getHTML(self):
        ''' Retrieve HTML ouput for this badge. Status must be set beforehand.'''
        if self.num==None:
            print 'No Value set for ' + self.name
            return ''
        verb = self.verbm if self.userIsMult else self.verbs
        if self.level == 'D':
            alt =("%s, %s | %s %s %d, %s reached the highest level"%
                  (self.name,
                   self.desc,
                   escape(self.user).encode('ascii', 'xmlcharrefreplace'),
                   verb,
                   self.num,
                   'have' if self.userIsMult else 'has'))
            return('<img src="%s%s%s.png" width=80px\n\talt  = "%s" \n\ttitle= "%s"\n/>\n'%
                   (self.path, self.icon, self.level, alt, alt))
        if self.level != None:
            alt = ("%s, %s | %s %s %d, %s %d (+%d) for next level"%
                   (self.name,
                    self.desc,
                    escape(self.user).encode('ascii', 'xmlcharrefreplace'),
                    verb, self.num,
                    'need' if self.userIsMult else 'needs',
                    self.goal,
                    self.goal-self.num))
            return('<img src="%s%s%s.png" width=80px\n\talt  = "%s" \n\ttitle= "%s"\n/>\n'%
                   (self.path, self.icon, self.level, alt, alt))
        else:
            return('<! No %s generated. %s %s only %d. %s %d (+%d) for level 1.>\n'%
                   (self.name,
                    escape(self.user).encode('ascii', 'xmlcharrefreplace'),
                    verb,
                    self.num,
                    'Need' if self.userIsMult else 'Needs',
                    self.goals[0],
                    self.goals[0]-self.num))

class stateBadge(badge):
    ''' Special class for state badges generated for specific countries.''' 
    def __init__(self, country, _iconPath=None):
        ''' Init badge with state name and optional icon path.'''
        self.name  = 'State award %s'%country
        self.desc = 'award for finding caches in a percentage of states in %s'% country
        self.verbs = 'has visited'
        self.verbm = 'have visited' 
        if _iconPath == None:
            self.iconPath = badgeManager.stateBadgeTemplate.path + badgeManager.stateBadgeTemplate.icon[:-1]
            self.iconPath = self.iconPath.replace('Canada',country)
        else:
            self.iconPath = _iconPath
        self.goals = []
        self.num=None
        self.setLevels([n*badgeManager.countryList[country]/8 for n in range(1,9)])
          
    def getHTML(self):
        ''' Retrieve HTML ouput for this badge. Status must be set beforehand.'''
        if self.num==None:
            print 'No Value set for ' + self.name
            return ''
        verb = self.verbm if self.userIsMult else self.verbs
        if self.level == 'D':
            alt = "%s, %s | %s %s %d, %s reached the highest level"%(self.name, self.desc, escape(self.user).encode('ascii', 'xmlcharrefreplace'), verb, self.num, 'have' if self.userIsMult else 'has')
            return '<img src="%s%s" width=80px\n\talt  = "%s" \n\ttitle= "%s"\n/>\n'%(self.iconPath, self.level, alt, alt)
        if self.level != None:
            alt = "%s, %s | %s %s %d, %s %d (+%d) for next level"%(self.name, self.desc,  escape(self.user).encode('ascii', 'xmlcharrefreplace'), verb, self.num, 'need' if self.userIsMult else 'needs', self.goal, self.goal-self.num)
            return '<img src="%s%s" width=80px\n\talt  = "%s" \n\ttitle= "%s"\n/>\n'%(self.iconPath, self.level, alt, alt)
        else:
            return '<! No %s generated. %s %s only %d. %s %d (+%d) for level 1.>\n'%(self.name,  escape(self.user).encode('ascii', 'xmlcharrefreplace'), verb, self.num, 'Need' if self.userIsMult else 'Needs', self.goals[0], self.goals[0]-self.num)