''' Parsers that operate on the profile page content.'''
from HTMLParser import HTMLParser

class CoinParser(HTMLParser):
    ''' Get information about coins and trackables from profile page content.'''
    def __init__(self):
        HTMLParser.__init__(self)
        self.stack=[]
        self.entity = None
        self.tableSig = ['html', 'body', 'div', 'div', 'table', 'tr', 'td']
        self.totalSig = ['html', 'body', 'div', 'div', 'table', 'tr', 'td',
                         'strong']
        self.atTB = False
        self.atTotal = False
        self.TBCount = 0
        self.TotalCount = 0
        self.CoinCount = 0
   
    def handle_charref(self, name):
        print 'charref ' + name   

    def handle_entityref(self, name):      
        self.entity = self.unescape('&'+name+';')

    def handle_starttag(self, name, attrs):      
        self.stack.append(name)
        #print self.stack
      
    def handle_endtag(self, name):
        #print str(self.stack) + ' <<<'
        self.entity = None 
        oldstack = self.stack
        try:
            while self.stack.pop() != name:
                pass        
        except:
            # this causes the parser to ingnore malformated html.
            # may cause errors in the future
            self.stack = oldstack
         
    def handle_data(self, data):            
        if "Travel Bug Dog Tags" in data:         
            self.atTB = True
            self.tempstack = str(self.stack)        
        elif self.atTB and self.tempstack == str(self.stack):
            self.TBCount = int(data.strip())
            self.atTB = False 
        elif "Total Trackables Moved" in data:
            self.tempstack= str(self.stack)
            self.atTotal = True
        elif self.atTotal and self.tempstack == str(self.stack):
            self.TotalCount = int(data.strip())
            self.atTotal = False
            self.CoinCount = self.TotalCount - self.TBCount


class OwnParser(HTMLParser):
    ''' Get information about own caches from profile page content'''
    def __init__(self):
        HTMLParser.__init__(self)
        self.stack=[]
        self.entity = None
        self.tableSig = ['div', 'table', 'tbody', 'tr', 'td', 'a']
        self.totalSig = ['html', 'body', 'div', 'div', 'table', 'tr', 'td',
                         'strong']
        self.atTB = False
        self.owncaches = []
        self.owncount = 0
        
    def handle_charref(self, name):
        print 'charref ' + name   

    def handle_entityref(self, name):      
        self.entity = self.unescape('&'+name+';')
    
    def handle_starttag(self, name, attrs):      
        self.stack.append(name)
        #print self.stack
        
    def handle_endtag(self, name):
        #print str(self.stack) + ' <<<'
        self.entity = None 
        oldstack = self.stack
        try:
            while self.stack.pop() != name:
                pass        
        except:
            # this causes the parser to ingnore malformated html.
            # may cause errors in the future
            self.stack = oldstack
         
    def handle_data(self, data):
        if self.stack == self.tableSig:
            self.owncount += 1
            self.owncaches.append(data.strip())
            #print 'Found ' + data.strip()
            #self.atTB = False 
        #elif "Total Trackables Moved" in data:
            #self.tempstack= str(self.stack)
            #self.atTotal = True
        #elif self.atTotal and self.tempstack == str(self.stack):
        #    self.TotalCount = int(data.strip())
        #    self.atTotal = False
        #    self.CoinCount = self.TotalCount - self.TBCount     