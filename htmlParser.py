from HTMLParser import HTMLParser

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
      self.limits=[]    
   
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
      # get the name
      if self.nameSig == self.stack:
         if self.entity:
            self.names.append(self.names.pop() + self.entity + data)
            self. entity = None
         else:
            self.names.append(data)            
            self.limits.append([])
            
      # get the description   
      if self.descSig == self.stack:
         if self.entity and self.stack != []:
            self.descs.append(self.descs.pop() + self.entity + data)
         elif data.strip(' ()').startswith('award'):
            self.descs.append(data)
      #get the levels      
      if self.stack == ['html', 'body', 'table', 'tr', 'td', 'table', 'tr', 'td', 'table', 'tbody', 'tr', 'td', 'img', 'br']:         
         limit = data.strip().partition('(' if '(' in data else '[')[2][:-1]         
         if limit.count('-') == 1 and limit.strip(' -+').count('-')== 1: #only one - and not as polarity sign
            self.limits[-1].append(limit.partition('-')[0].strip(' km'))            
            #print self.limits[-1]
         elif limit.count('-') == 1 and limit.strip(' -+').count('-')== 0: #only one negative number
            self.limits[-1].append(limit.strip(' +km'))            
            #print self.limits[-1]
         elif limit.count('-') == 0 and limit.count(',') == 0: # just a single positive number
            self.limits[-1].append(limit.strip(' +km'))
            #print self.limits[-1]
         elif limit.count('-') == 3: # two negative numbers
            self.limits[-1].append('-' + limit[1:].partition('-')[0].strip(' km'))            
            #print self.limits[-1]
         elif limit.count(',') == 1: #new limit notation
            self.limits[-1].append(limit.partition(',')[0].strip(' km'))
         else:
            print limit
            
         #self.limits.append(limit)
         #self.limits[-1].append()         
         #print data.strip() + ' -> ' + data.strip().partition('(' if '(' in data else '[')[2][:-1]
         #print self.stack

   def finish(self):
      self.names = [a.strip() for a in self.names]
      self.descs = [a.strip(' ()') for a in self.descs]
