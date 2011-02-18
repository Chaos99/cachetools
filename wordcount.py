#!python
# -*- coding: UTF-8 -*-

#env GIT_AUTHOR_DATE='Thu Feb 17 17:00:00 2011 +0200' GIT_COMMITTER_DATE='Thu Feb 17 17:00:00 2011 +2000' git commit -a -m ""

import sys

from badges import *
from htmlParser import *
from gpxParser import *
from ConfigParser import SafeConfigParser as ConfigParser

if not len(sys.argv) == 2:
   print "Usage: python [-i] <gpx-file> "
   sys.exit()

confParser = ConfigParser({'badgeHTMLfile':'badges.html','proxy':None})
confParser.read('config')

try:
   pers.username = confParser.get('DEFAULT', 'username')
   pers.password = confParser.get('DEFAULT', 'password')
except:
   print "No username and/or password given in config file"
   sys.exit()


p = gpxParser(pers)
h = htmlParser()

f = open(sys.argv[1],'r')
p.feed(f.read(), 1)
f.close()

badgeHTMLname = confParser.get('DEFAULT', 'badgeHTMLfile')

try:
   f = open(badgeHTMLname,'r')
except:
   print "Badge definition HTML file could not be read from %s"%badgeHTMLname

h.feed(f.read())
h.close()
f.close()

print "All: "+str(pers.count)+"  With logs: "+str(pers.logcount)+"  with own logs: "+str(pers.ownlogcount)+"  thereof found: "+str(pers.ownfoundlogcount)
avgWordCount = pers.wordcount / pers.ownfoundlogcount if pers.ownfoundlogcount > 0 else 0
   
print "Average  word count: " + str(avgWordCount)


#print "Last 5 Logs: " + str(pers.words[-5])+ ' '+ str(pers.words[-4])+ ' '+ str(pers.words[-3])+ ' '+ str(pers.words[-2])+ ' '+ str(pers.words[-1])


#badge.setUser(pers.username, True)
#badge.setPath('./')

badgeManager.setCredentials(pers.username, True)
badgeManager.populate(h.names,h.descs,h.icons,h.paths,h.limits)
badgeManager.setStatus('Author', avgWordCount)
badgeManager.getHTML('Author')
for k,v in zip(pers.typeCount.keys(), pers.typeCount.values()):
   if not 'Event' in k:
      badgeManager.setStatus(k[:5],v)
   # Event is ambigous, need special attentions
   else:
      if 'Mega' in k:
         badgeManager.setStatus('Mega',v)
      else: #the tricky part: the normal event without the mega
         for b in badgeManager.badges:
            if 'event' in b.desc.lower() and not 'mega' in b.desc.lower() and not 'CITO' in b.desc.lower():
               b.setStatus(v)
               break
         
for k,v in zip(pers.containerCount.keys(), pers.containerCount.values()):   
   badgeManager.setStatus(k[:5],v)
   

badgeManager.setStatus('Lost',pers.tenCount)
badgeManager.setStatus('Adventur',pers.HCCCount)
badgeManager.setStatus('FTF',pers.FTFcount)
badgeManager.setStatus('Coin',67)
badgeManager.setStatus('Travelbug',50)
 
text = badgeManager.getHTML('ALL')

import spider
spider.ConnectionManager.setProxy(confParser.get('DEFAULT', 'proxy'))
c = spider.ConnectionManager(pers.username, pers.password)

#c.logon()
r = c.getMyCoinList()


f = open("profile.html",'w')
for t in text:
   f.write(t)
f.close()

#bb = badge('Traditional Badge', 'awarded for finding traditional caches','has found','have found','Trad') 
#bb.setLevels([25,50,75,100,150,200,500,1000])
#bb.setStatus(235)
#print bb.getHTML()

