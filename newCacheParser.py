# -*- coding: UTF-8 -*-
from HTMLParser import HTMLParser
import re

class newCacheParser(HTMLParser):
    ''' Parser for the geocaching profile page to get new cache logs.'''
    def __init__(self):
        HTMLParser.__init__(self)
        self.stack=[]
        self.entity = None
        self.guid = ""
        self.tableSig = ['html', 'body', 'form', 'div', 'div', 'div', 'div', 'div', 'div', 'table']      
        self.inTable = False
        self.rowCount =0
        self.entries = []
        self.logToFollow = False
        self.nameToFollow = False
   
    def feed(self, text):
        # reset al previous values
        #self.reset()
        self.__init__()      
        # remove scripts and spans, cause they are malformated
        text = re.compile("<script([^>]*)>.*?</script>", re.DOTALL).sub("", text)
        text = re.compile("<iframe([^>]*)>.*?</iframe>", re.DOTALL).sub("", text)
        #text = re.compile("<span([^>]*)>.*?</span>", re.DOTALL).sub("", text)
        #open("result2.html","w").write(text)
        try:
            HTMLParser.feed(self, text)
        except Exception as e:
            print e
            raise
      
    def handle_charref(self, name):
        #print 'charref ' + name
        self.entity = chr(int(name))
      

    def handle_entityref(self, name):
        #print "Entity called for " + name
        self.entity = self.unescape('&'+name+';')
        #self.entity = "NN"
        #print self.entity

    def handle_starttag(self, name, attrs):      
        self.stack.append(name)
        #print self.stack
        #we are exclusively interested in the tables contents
        if self.stack[:len(self.tableSig)] == self.tableSig:
            self.inTable = True
        if self.inTable and name == 'tr':         
            self.startRow()
        elif self.inTable and self.stack[-3:] == ['tr','td','img']:
            self.eType = [a[1] for a in attrs if a[0]=='alt'][0] 
        elif self.inTable and self.stack[-3:] == ['tr','td','a']:         
            src = [a[1] for a in attrs if a[0]=='href'][0]
            if "cache_details" in src:
                self.guid = src[-36:]
                self.nameToFollow = True
            elif "log.aspx" in src:
                self.luid = src[-36:]
                self.logToFollow = True
        elif self.inTable and self.stack[-4:] == ['tr','td','a','img']:
            title = [a[1] for a in attrs if a[0]=='title'][0]         
            self.ctype = title
      
    def handle_endtag(self, name):      
        #print str(self.stack) + ' <<<'     
        self.entity = None 
        self.nameToFollow = False
        self.logToFollow = False
        
        if (self.stack[:len(self.tableSig)] == self.tableSig) and name == "table":
            self.inTable = False
        if self.inTable and name == 'tr':         
            self.stopRow()
        oldstack = self.stack
        try:
            while self.stack.pop() != name:
                pass        
        except:
            #print 'Malformated html input at endtag ' + name +'\n resetting stack'
            # this causes the parser to ingnore malformated html. may cause errors in the future
            self.stack = oldstack
        
            
    def handle_data(self, data):
        #we are exclusively interested in the tables contents
        if self.stack[:len(self.tableSig)] == self.tableSig:
            if self.stack[-2:] == ['tr','td'] and self.date == '':
                self.date = data.strip()
            if self.stack[-3:] == ['tr','td','a'] and self.nameToFollow:            
                if self.entity != None:
                    try:
                        self.cname = (self.cname + self.entity + data)
                    except UnicodeDecodeError:
                        print 'Character encoding error'
                        self.cname = (self.cname + data)
                    self. entity = None
                else:
                    self.cname = data
                
        
    def startRow(self):
        self.rowCount +=1
        self.eType = "None"
        self.date=''
        self.cname = ''
        
    def stopRow(self):
        self.entries.append([self.eType, self.date, self.guid, self.cname, self.ctype, self.luid])