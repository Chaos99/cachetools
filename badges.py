from cgi import escape

class badgeManager():
   badges = []
   user = ""
   isMultiple=True
   stateBadgeTemplate = None
   countryList = {}
   
   @classmethod
   def populate(cls, h): 
      if cls.user != '':
         badge.setUser(cls.user,cls.isMultiple)
      else:
         print 'must set user before populating badge list'
      for (n,d,i,p,l) in zip(h.names,h.descs,h.icons,h.paths,h.limits):
         #print n + ' ' + d
         #print p + '/' + i
         #print l
         ba = badge(n,d, _icon=i)
         ba.overridePath(p)
         ba.setLevels(l)
         if n == "State Badges":
            cls.stateBadgeTemplate = ba
         else:
            cls.badges.append(ba)
         
   @classmethod
   def addBadge(cls, _badge):
      cls.badges.append(_badge)
   
   @classmethod
   def setStatus(cls, name, value):
      try:
         a = cls.getBadge(name)
      except:
         #print "Couldnt set Value to %d."%(value)
         raise      
      a.setStatus(value)
      return a.getHTML()
   
   @classmethod
   def getHTML(cls, name='ALL'):
      ret = []
      for a in cls.badges:
         if name.lower() in a.name.lower() or name.lower()=='all':
            ret.append(a.getHTML())      
      return ret
   
   @classmethod
   def setCredentials(cls, user, isMultiple=True):
      cls.user = user
      cls.isMultiple = isMultiple
   
   @classmethod
   def getBadge(cls, name):
      #horrible hack to solve event issue
      if name == 'event': name='social' 
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
         return reduce(lambda x,y: x if len(x.name) < len(y.name) else y, candidates)
      else: 
         #print "Sorry, no match for badge name %s"%name
         raise NameError('BadgeName')

   @classmethod
   def setCountryList(cls, clist):
      cdict = {}
      for line in clist.split('\n'):
         cdict[line.partition(',')[0].strip()] = int(line.partition(',')[2].strip())
      cls.countryList = cdict

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
      self.num=None

   
   @classmethod
   def setUser(_class, _user,_m):
      _class.user= _user      
      _class.userIsMult = _m
     
   @classmethod
   def setPath(_class, _path):
      _class.path= _path
   
   def setLevels(self, _goals):
      if len(_goals) == 8:
         self.goals= [int(g) for g in _goals]         
      else:
         print "Not a valid list of level goals" + str(_goals)

   
   def setStatus(self, _num):
      self.num = _num
      #if self.goals.isempty() :
      self.level = None
      if self.goals[1] > self.goals[0]:
         for g,l in zip(self.goals, self.levels):
            if _num >= g:
               self.level = l
               self.goal = self.goals[self.goals.index(g)+1] if l != 'D' else 0
            else:
               pass
      else:
         for g,l in zip(self.goals, self.levels):
            if _num <= g:
               self.level = l
               self.goal = self.goals[self.goals.index(g)+1] if l != 'D' else 0
            else:
               pass
   
   def overridePath(self, _path):
      self.path= _path
  
   def getHTML(self):
      if self.num==None:
         print 'No Value set for ' + self.name
         return ''
      verb = self.verbm if self.userIsMult else self.verbs
      if self.level == 'D':
         alt = "%s, %s | %s %s %d, %s reached the highest level"%(self.name, self.desc, escape(self.user).encode('ascii', 'xmlcharrefreplace'), verb, self.num, 'have' if self.userIsMult else 'has')
         return '<img src="%s%s%s.png" width=80px\n\talt  = "%s" \n\ttitle= "%s"\n/>\n'%(self.path, self.icon, self.level, alt, alt)
      if self.level != None:
         alt = "%s, %s | %s %s %d, %s %d (+%d) for next level"%(self.name, self.desc,  escape(self.user).encode('ascii', 'xmlcharrefreplace'), verb, self.num, 'need' if self.userIsMult else 'needs', self.goal, self.goal-self.num)
         return '<img src="%s%s%s.png" width=80px\n\talt  = "%s" \n\ttitle= "%s"\n/>\n'%(self.path, self.icon, self.level, alt, alt)
      else:
         return '<! No %s generated. %s %s only %d. %s %d (+%d) for level 1.>\n'%(self.name,  escape(self.user).encode('ascii', 'xmlcharrefreplace'), verb, self.num, 'Need' if self.userIsMult else 'Needs', self.goals[0], self.goals[0]-self.num)

class stateBadge(badge):
   
   def __init__(self, country, _iconPath=None):
      self.name  = 'State award %s'%country
      self.desc = 'award for finding caches in a percentage of states in %s'%country
      self.verbs = 'has visited'
      self.verbm = 'have visited' 
      if _iconPath == None:
         self.iconPath = badgeManager.stateBadgeTemplate.path + badgeManager.stateBadgeTemplate.icon
      else:
         self.iconPath = _iconPath
      self.goals = []
      self.num=None
      self.setLevels([n*badgeManager.countryList[country]/8 for n in range(1,9)])
    
   def getHTML(self):
      if self.num==None:
         print 'No Value set for ' + self.name
         return ''
      verb = self.verbm if self.userIsMult else self.verbs
      if self.level == 'D':
         alt = "%s, %s | %s %s %d, %s reached the highest level"%(self.name, self.desc, escape(self.user).encode('ascii', 'xmlcharrefreplace'), verb, self.num, 'have' if self.userIsMult else 'has')
         return '<img src="%s%s%s.png" width=80px\n\talt  = "%s" \n\ttitle= "%s"\n/>\n'%(self.path, self.icon, self.level, alt, alt)
      if self.level != None:
         alt = "%s, %s | %s %s %d, %s %d (+%d) for next level"%(self.name, self.desc,  escape(self.user).encode('ascii', 'xmlcharrefreplace'), verb, self.num, 'need' if self.userIsMult else 'needs', self.goal, self.goal-self.num)
         return '<img src="%s%s%s.png" width=80px\n\talt  = "%s" \n\ttitle= "%s"\n/>\n'%(self.path, self.icon, self.level, alt, alt)
      else:
         return '<! No %s generated. %s %s only %d. %s %d (+%d) for level 1.>\n'%(self.name,  escape(self.user).encode('ascii', 'xmlcharrefreplace'), verb, self.num, 'Need' if self.userIsMult else 'Needs', self.goals[0], self.goals[0]-self.num)