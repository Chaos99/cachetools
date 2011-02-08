class badgeManager():
   badges = []
   user = ""
   isMultiple=True
   
   @classmethod
   def populate(cls, names, descs, icons, paths, levels):
      if cls.user != '':
         badge.setUser(cls.user,cls.isMultiple)
      else:
         print 'must set user before populating badge list'
      for (n,d,i,p,l) in zip(names,descs,icons,paths,levels):
         #print n + ' ' + d
         #print p + '/' + i
         #print l
         ba = badge(n,d, _icon=i)
         ba.overridePath(p)
         ba.setLevels(l)
         cls.badges.append(ba)
   
   @classmethod
   def setStatus(cls, name, value):
      for a in cls.badges:
         if name.lower() in a.name.lower():
            a.setStatus(value)
            return a.getHTML()
         #no match in names? try in descriptions      
         elif name.lower() in a.desc.lower():
            a.setStatus(value)
            return a.getHTML()
      print 'Sorry, no matsch for badge name "' + name + '"'
   
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
      for a in cls.badges:
         if name in a.name:
            return a
         #no match in names? try in descriptions      
         elif name in a.desc:
            return a
      print 'Sorry, no matsch for badge name "' + name + '"'


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
      for g,l in zip(self.goals, self.levels):
         if _num >= g:
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
         alt = "%s, %s | %s %s %d, %s reached the highest level>"%(self.name, self.desc, self.user, verb, self.num, 'have' if self.userIsMult else 'has')
         return '<img src="%s%s%s.png" \n\talt  = "%s" \n\ttitle= "%s"\n/>'%(self.path, self.icon, self.level, alt, alt)
      if self.level != None:
         alt = "%s, %s | %s %s %d, %s %d (+%d) for next level>"%(self.name, self.desc, self.user, verb, self.num, 'need' if self.userIsMult else 'needs', self.goal, self.goal-self.num)
         return '<img src="%s%s%s.png" \n\talt  = "%s" \n\ttitle= "%s"\n/>'%(self.path, self.icon, self.level, alt, alt)
      else:
         return '<! No %s generated. %s %s only %d. %s %d (+%d) for level 1.>'%(self.name, self.user, verb, self.num, 'Need' if self.userIsMult else 'Needs', self.goals[0], self.goals[0]-self.num)
