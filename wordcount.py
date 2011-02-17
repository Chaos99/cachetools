#!python
# -*- coding: UTF-8 -*-

#env GIT_AUTHOR_DATE='Mon Feb 07 17:01:00 2011 +0200' GIT_COMMITTER_DATE='Mon Feb 07 17:01:00 2011 +2000' git commit -a -m 'Merge and relocated counting to /wpt tag'

import sys

from badges import *
from htmlParser import *
from gpxParser import *

if not sys.argv and not len(sys.argv) == 3:
   print "Usage: python [-i] <gpx-file> <username> <badge html file>"
   sys.exit()

pers.username = sys.argv[2]

p = gpxParser(pers)
h = htmlParser()

f = open(sys.argv[1],'r')
p.feed(f.read(), 1)
f.close()

f = open(sys.argv[3],'r')
h.feed(f.read())
h.close()
f.close()

print "All: "+str(pers.count)+"  With logs: "+str(pers.logcount)+"  with own logs: "+str(pers.ownlogcount)+"  thereof found: "+str(pers.ownfoundlogcount)
print "Average  word count: " + str(pers.wordcount / pers.ownfoundlogcount)


#print "Last 5 Logs: " + str(pers.words[-5])+ ' '+ str(pers.words[-4])+ ' '+ str(pers.words[-3])+ ' '+ str(pers.words[-2])+ ' '+ str(pers.words[-1])


#badge.setUser(pers.username, True)
#badge.setPath('./')

badgeManager.setCredentials(pers.username, True)
badgeManager.populate(h.names,h.descs,h.icons,h.paths,h.limits)
badgeManager.setStatus('Author', pers.wordcount / pers.ownfoundlogcount)
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
 
text = badgeManager.getHTML('ALL')

f = open("profile.html",'w')
for t in text:
   f.write(t)
f.close()

#bb = badge('Traditional Badge', 'awarded for finding traditional caches','has found','have found','Trad') 
#bb.setLevels([25,50,75,100,150,200,500,1000])
#bb.setStatus(235)
#print bb.getHTML()

