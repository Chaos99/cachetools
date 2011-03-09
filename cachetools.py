#!python
# -*- coding: UTF-8 -*-

#env GIT_AUTHOR_DATE='Thu Feb 17 17:00:00 2011 +0200' GIT_COMMITTER_DATE='Thu Feb 17 17:00:00 2011 +2000' git commit -a -m ""

import sys
import spider
import re
import copy

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

##### BADGE DEFINITION #####

try:
   f = open(badgeHTMLname,'r')
except:
   print "Badge definition HTML file could not be read from %s"%badgeHTMLname

h.feed(f.read())
h.close()
f.close()

# create badges
print "All: "+str(pers.count)+"  With logs: "+str(pers.logcount)+"  with own logs: "+str(pers.ownlogcount)+"  thereof found: "+str(pers.ownfoundlogcount)
badgeManager.setCredentials(pers.username, True)
badgeManager.populate(h) #creates the standard badges from the website content

##### LOGS ####

avgWordCount = pers.wordcount / pers.ownfoundlogcount if pers.ownfoundlogcount > 0 else 0
print "Average  word count: " + str(avgWordCount)
badgeManager.setStatus('Author', avgWordCount)

#### OVERALL COUNT #####

badgeManager.setStatus('Geocacher', pers.ownfoundlogcount)
print "Geocaches " + str(pers.ownfoundlogcount)

##### TYPES #####
print '\n'
types = ['Traditional Cache', 'Multi-cache', 'Unknown Cache', 'Letterbox Hybrid', 'Earthcache', 'Wherigo Cache', 'CITO Event Cache','Event Cache','Virtual Cache','Mega Social Event Cache','Benchmark','Waymark','Webcam Cache','Project Ape Cache']

for t in types:
   if t in pers.typeCount.keys():       
      key = filter(lambda x: t[:5].lower() in x.lower(), pers.typeCount.keys())
      if len(key) == 1:
         try:
            badgeManager.setStatus(t[:5].lower(),pers.typeCount[key[0]])
            print t + ' ' + str(pers.typeCount[key[0]])
         except NameError('BadgeName'):
            print "No Match for Cachetype %s found. Nothing was set."%t
            pass
      else:
         print "Ambiquious type name '"+t+"', found (gpx: "+str(key)+") aborting..."
         pass  
   else:
      try:
         badgeManager.setStatus(t[:5].lower(),0)
         print t + ' ' + str(0)
      except NameError('BadgeName'):
            print "No Match for Cachetype %s found. Nothing was set."%t
            pass
      
badgeManager.setStatus('Lost',pers.LostnFoundCount)
print '10 Years! Cache ' + str(pers.LostnFoundCount)
##### CONTAINERS #####3
print '\n',
for k,v in zip(pers.containerCount.keys(), pers.containerCount.values()):
   try:
      badgeManager.setStatus(k[:5],v)
      print k + ' ' + str(v)
   except NameError:
            print k + " No Match"
            pass
   

######### D/T Matrix #############
print '\n\t',
dif = ter = [1,1.5,2,2.5,3,3.5,4,4.5,5]
mcount = 0;
for d in dif:
   for t in ter:
      r = pers.Matrix[d][t]
      print"%3d"%(r),
      if r > 0: mcount += 1 
   print "\n\n\t",
print "Found %d of 81 D/T combinations"%mcount

badgeManager.setStatus('Matrix',mcount)

###### OTHERS #####
print '\n',
badgeManager.setStatus('Adventur',pers.HCCCount)
print 'HCC Caches ' + str(pers.HCCCount)
badgeManager.setStatus('FTF',pers.FTFcount)
print 'FTF Caches ' + str(pers.FTFcount)

#badgeManager.setStatus('Travelling',2)
badgeManager.setStatus('Owner', 9)
#badgeManager.setStatus('Owner', 1)
badgeManager.setStatus('Clouds',1715)
#badgeManager.setStatus('Clouds',1050)
badgeManager.setStatus('Gound',-4)
badgeManager.setStatus('Busy',22)
#badgeManager.setStatus('Busy',10)
badgeManager.setStatus('Daily',93)
#badgeManager.setStatus('Daily',4)
badgeManager.setStatus('Calendar',210)
#badgeManager.setStatus('Calendar',34)
badgeManager.setStatus('Scuba',0)
badgeManager.setStatus('Host',0)
badgeManager.setStatus('Distance',18418)
#badgeManager.setStatus('Distance',2071)

#badgeManager.setStatus('Matrix',18)
#badgeManager.setStatus('State',10)

##### COUNTRIES #######
print '\n',
badgeManager.setStatus('Travelling',len(pers.countryList))
print 'Countries traveled ' + str(len(pers.countryList))

try:
   f = open("statelist.txt",'r')
   r = f.read()
   f.close()
except:
   r = c.getCountryList()
   f = open("statelist.txt",'w')
   f.write(r)
   f.close()

badgeManager.setCountryList(r)
for country in pers.countryList.keys():   
   cBadge = stateBadge(country)
   cBadge.setStatus(len(pers.stateList[country])) 
   badgeManager.addBadge(cBadge)
   
   print 'Visited ' + str(len(pers.stateList[country])) + ' state(s) in ' + country

#### COINS ##########
print '\n',
# debug version of caching
# force new downlad by deleting cached file
try:
   f = open("profile.html",'r')
   r = f.read()
   f.close()
except:
   print 'No Coin list cached, retrieving new data ...'
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
print "Coins " + str(coinP.CoinCount)
badgeManager.setStatus('Travelbug',coinP.TBCount)
print "Travelbugs " + str(coinP.TBCount)


#### OUTPUT ##########

badgesEarned = badgeManager.getHTML('ALL')

text='<center>\n'
for t in [b for b in badgesEarned if 'D.png' in b or "level=D" in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'E.png' in b or "level=E" in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'Sa.png' in b or "level=Sa" in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'R.png' in b or "level=R" in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'P.png' in b or "level=P" in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'G.png' in b or "level=G" in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'S.png' in b or "level=S" in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'B.png' in b or "level=B" in b]:
   text += t
text += '\n<br/>\n'
for t in [b for b in badgesEarned if 'generated' in b]:
   text += t
text += '\n</center>'
c.saveTemp(text)



