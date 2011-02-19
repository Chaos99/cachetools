#!python
# -*- coding: UTF-8 -*-

#env GIT_AUTHOR_DATE='Thu Feb 17 17:00:00 2011 +0200' GIT_COMMITTER_DATE='Thu Feb 17 17:00:00 2011 +2000' git commit -a -m ""

import sys
import spider
import re

from badges import *
from htmlParser import *
from gpxParser import *
from ConfigParser import SafeConfigParser as ConfigParser

if not len(sys.argv) == 2:
   print "Usage: python [-i] <gpx-file> "
   sys.exit()

confParser = ConfigParser({'badgeHTMLfile':'badges.html','proxy':None})
if not confParser.read('config.cfg'):
    print "No config file found. A new one was generated, please fill in username and password"
    f = open('config.cfg','w')
    f.write('[DEFAULT]\n\n')
    f.write('username = \n')
    f.write('password = \n')
    f.write('badgeHTMLfile = badges.html\n')
    f.write('proxy = None\n')
    f.flush()
    f.close()
    sys.exit()

try:
   pers.username = confParser.get('DEFAULT', 'username')
   pers.password = confParser.get('DEFAULT', 'password')
except:
   print "No username and/or password given in config file"
   sys.exit()

badgeHTMLname = confParser.get('DEFAULT', 'badgeHTMLfile')

spider.ConnectionManager.setProxy(confParser.get('DEFAULT', 'proxy'))
c = spider.ConnectionManager(pers.username, pers.password)

p = gpxParser(pers)
h = htmlParser()

f = open(sys.argv[1],'r')
p.feed(f.read(), 1)
f.close()



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

# create badges

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
 


# debug version of caching
# force new downlad by deleting cached file
try:
   f = open("profile.html",'r')
   r = f.read()
   f.close()
except:
   r = c.getMyCoinList()
   f = open("profile.html",'w')
   f.write(r)
   f.close()

# remove scripts and spans, cause they are malformated
r = re.compile("<script([^>]*)>.*?</script>", re.DOTALL).sub("", r)
r = re.compile("<span([^>]*)>.*?</span>", re.DOTALL).sub("", r)

from coinParser import coinParser
coinP = coinParser()
coinP.feed(r)

badgeManager.setStatus('Coin',coinP.CoinCount)
badgeManager.setStatus('Travelbug',coinP.TBCount)

badgesEarned = badgeManager.getHTML('ALL')

text='<center>\n'
for t in [b for b in badgesEarned if 'D.png' in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'E.png' in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'Sa.png' in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'R.png' in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'P.png' in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'G.png' in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'S.png' in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'B.png' in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'generated' in b]:
   text += t
text += '\n</center>'
c.saveTemp(text)


