#!python
# -*- coding: UTF-8 -*-
import sys

from badges import *
from htmlParser import *
from gpxParser import *


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
   badgeManager.setStatus(k[:5],v)
 
badgeManager.getHTML('Tradi')

#bb = badge('Traditional Badge', 'awarded for finding traditional caches','has found','have found','Trad') 
#bb.setLevels([25,50,75,100,150,200,500,1000])
#bb.setStatus(235)
#print bb.getHTML()

