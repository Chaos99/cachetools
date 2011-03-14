from HTMLParser import HTMLParser
import re

class printParser(HTMLParser):

   def __init__(self):
      HTMLParser.__init__(self)
      self.stack=[]
      self.entity = None
      self.typeSig =  ['html', 'body', 'form', 'div', 'div', 'h2', 'img']
      self.nameSig = ['html', 'body', 'form', 'div', 'div', 'div', 'h1']
      self.descSig = ['html', 'body', 'table', 'tr', 'td', 'table', 'tr', 'td', 'table', 'tbody', 'tr', 'td']
      self.iconSig = ['html', 'body', 'table', 'tr', 'td', 'table', 'tr', 'td', 'table', 'tbody', 'tr', 'td']
      self.names=[]
      self.descs=[]
      self.icons=[]
      self.paths=[]
      self.limits=[]
   
   def feed(self, text):
      # remove scripts and spans, cause they are malformated
      text = re.compile("<script([^>]*)>.*?</script>", re.DOTALL).sub("", text)
      text = re.compile("<span([^>]*)>.*?</span>", re.DOTALL).sub("", text)
      HTMLParser.feed(self, text)
   
   def handle_charref(self, name):
      #print 'charref ' + name
      pass   

   def handle_entityref(self, name):      
      self.entity = self.unescape('&'+name+';')

   def handle_starttag(self, name, attrs):
      self.stack.append(name)
      if self.stack == self.typeSig:
         self.ctype = [a[1] for a in attrs if a[0] == 'alt'] 
      #if name == "img" and 'alt' in [a[0] for a in attrs] and 'Traditional Cache' in [a[1]  for a in attrs if (a[0] == "alt")]:
      #   print "Type found in attrs of: " + str(self.stack)
      
      #print str(self.stack)
      
   def handle_endtag(self, name):
      self.entity = None
      if name == 'html':
         self.finish()
      if name not in self.stack:
         print "Malformated HTML at %s, Stack: %s"%(name,str(self.stack))
      else:
         while self.stack.pop() != name:
            pass         

   def handle_data(self, data):
      # get the name
      if data.strip() == 'GC2NN0H':
         print "CID found at: " + str(self.stack)
      

   def finish(self):
      print "Done"
      pass
