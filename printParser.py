# -*- coding: UTF-8 -*-

from HTMLParser import HTMLParser
import re

from collections import defaultdict

class printParser(HTMLParser):

   def __init__(self):
      HTMLParser.__init__(self)
      self.stack=[]
      self.entity = None      
      self.sig = {\
         "type" :       ['html', 'body', 'form', 'div', 'div', 'h2', 'img'],\
         "cid" :        ['html', 'body', 'form', 'div', 'div', 'div', 'h1'],\
         "name" :       ['html', 'body', 'form', 'div', 'div', 'h2'],\
         "owner" :      ['html', 'body', 'form', 'div', 'div', 'div', 'p'],\
         "placed" :     ['html', 'body', 'form', 'div', 'div', 'div', 'p'],\
         "container":   ['html', 'body', 'form', 'div', 'div', 'div', 'p', 'small'],\
         "difficulty" : ['html', 'body', 'form', 'div', 'div', 'div', 'p', 'img'],\
         "diff_marker": ['html', 'body', 'form', 'div', 'div', 'div', 'p', 'strong'],\
         "content":     ['html', 'body', 'form', 'div', 'div', 'div', 'div', 'div']\
      }
      self.result = defaultdict(lambda: "")
      
      self.atDif=False
      self.atTer=False
      self.insDes = False
      self.inlDes = False
      self.inHint = False
      self.recording = False
      self.rec = ""
         
   def feed(self, text):
      # reset al previous values
      #self.reset()
      self.__init__()
      # remove scripts and spans, cause they are malformated
      text = re.compile("<script([^>]*)>.*?</script>", re.DOTALL).sub("", text)
      text = re.compile("<span([^>]*)>.*?</span>", re.DOTALL).sub("", text)
      HTMLParser.feed(self, text)
   
   def handle_charref(self, name):
      if self.recording:
         self.rec += name
      #print 'charref ' + name
      pass   

   def handle_entityref(self, name):
      if self.recording:
         self.rec += name
      self.entity = self.unescape('&'+name+';')
      
         
   def handle_starttag(self, name, attrs):
      if self.recording:
         self.rec += "<"+name
         if attrs:
            for a,b in attrs:
               self.rec += ' '+a+'="'+b+'"'
         self.rec += ">"
         
      #print self.stack
      self.stack.append(name)
      if self.stack == self.sig["type"] and self.result["type"] == "":
         self.result["type"] = [a[1] for a in attrs if a[0] == 'alt'][0]
      elif self.stack == self.sig["difficulty"] and self.result["difficulty"] == "" and self.atDif:
         self.result["difficulty"] = [a[1].split()[0] for a in attrs if a[0] == 'alt'][0]
         self.atDif = False
      elif self.stack == self.sig["difficulty"] and self.result["terrain"] == "" and self.atTer:
         self.result["terrain"] = [a[1].split()[0] for a in attrs if a[0] == 'alt'][0]
         self.atTer = False
      elif self.stack == self.sig["content"] and (self.insDes or self.inlDes or self.inHint):
         #print "Start recording" + " at: " + str(self.stack)
         self.recording = True
         self.backupStack = str(self.stack)
         
      #if name == "img" and 'alt' in [a[0] for a in attrs] and '2.5 out of 5' in [a[1]  for a in attrs if (a[0] == "alt")] and self.atDif:
      #   print "Difficult found in attrs of: " + str(self.stack)
      #   self.atDif = False
      #print str(self.stack)

   def handle_endtag(self, name):
      
      self.entity = None
      if name == 'html':
         self.finish()
         
      if self.recording and str(self.stack) == str(self.backupStack):
         #print "Stop recording" + " at: " + str(self.stack) + " with: " + self.rec
         if self.insDes:
            self.result["shortDescription"]=self.rec.strip()
            self.insDes = False            
         elif self.inlDes:
            self.result["longDescription"]=self.rec.strip()
            self.inlDes = False
         elif self.inHint:
            self.result["Hint"]=self.rec.strip()
            self.inHint = False
         
         self.recording = False
         self.rec = ""
      elif self.recording:
         self.rec += "</"+name+">"
         
      if name not in self.stack:
         print "Malformated HTML at %s, Stack: %s"%(name,str(self.stack))
      else:
         while self.stack.pop() != name:
            pass

   def handle_data(self, data):
      if self.recording:
         self.rec += data
      #print self.stack
      # get the name
      if self.stack == self.sig["cid"] and self.result["cid"] == "":
         self.result["cid"] = data.strip()
      elif self.stack == self.sig["name"] and self.result["name"] == "":
         self.result["name"] = data.strip()
      elif self.stack == self.sig["owner"]:
         if "Placed by" in data and self.result["owner"] == "":
            self.result["owner"] = data.strip()[10:].strip()
         elif "Date" in data and self.result["date"] == "":
            self.result["date"] = data.strip()[13:].strip()
         elif "UTM" in data and self.result["utmcoord"] == "":
            self.result["utmcoord"] = data.strip()[4:].strip()
         elif "°" in data and self.result["coord"] == "":
            self.result["coord"] = data.strip()
      elif self.stack == self.sig["container"] and self.result["container"] == "":
         self.result["container"] = data.strip()[1:-1] 
      elif self.stack == self.sig["diff_marker"] and "Difficulty" in data:
         self.atDif = True
      elif self.stack == self.sig["diff_marker"] and "Terrain" in data:
         self.atTer = True
      elif self.lasttag == "h2" and "Short Description" in data:
         self.insDes = True
      elif self.lasttag == "h2" and "Long Description" in data:
         self.inlDes = True
      elif self.lasttag == "h2" and "Additional Hints" in data:
         self.inHint = True
         
      # debug: find signature   
      #if 'blub' in data.strip():
         #print "Short description found at: " + str(self.stack)
         #self.atDif = True
         
      

   def finish(self):
      print "Done"
      pass
