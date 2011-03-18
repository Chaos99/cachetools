#!python
# -*- coding: UTF-8 -*-

#env GIT_AUTHOR_DATE='Thu Mar 10 17:02:00 2011 +0200' GIT_COMMITTER_DATE='Thu Mar 10 17:03:00 2011 +2000' git commit -a -m ""

import sys
import re
import os
import getopt

from badges import *
from badgeParser import *
from gpxParser import *
from spider import *
from geoTools import geoTools
from ConfigParser import SafeConfigParser as ConfigParser
from coinParser import coinParser
from newCacheParser import newCacheParser

def checkUpdates(conMngr, gpxPinst, originalGPX):
   nCPinst = newCacheParser() 
   try:
      #ask connection manager for an updated list of finds
      nCPinst.feed(conMngr.getCacheList())
   except Exception():
      print "Couldn't download cache list. Maybe there are connection problems?\n Continuing without updating."
      gpxPinst.feed('</gpx>',1)
      return
   found = [a.url[-36:] for a in gpxPinst.allCaches]
   update = [unicode(b[2]) for b in nCPinst.entries if "Found" in b[0]]
   print "Found %d Cache logs online"%len(update),
   [b[3] for b in nCPinst.entries if "Found" in b[0]]
   new = [b for b in update if b not in found]
   if len(new) < len(found):
      print ", thereof %d were new."%len(new)      
      if new:
         first = True
         #new will have the newest log first; reverse it so it's last in the file
         new.reverse()
         for guid in new:
            if first:
               try:
                  #ask connection manager for the gpx file of the new cache
                  newGPX = conMngr.getSingleGPX(guid)
                  first = False
               except Exception():
                  print "Couldn't download cache gpx. Maybe there are connection problems?\n Aborting the update and continuing without."
                  gpxPinst.feed('</gpx>',1)
                  return
            else:
               newGPX = conMngr.combineGPX(newGPX, conMngr.getSingleGPX(guid))
         print "Parsing new caches ...",      
         gpxPinst.feed(newGPX[newGPX.find('<wpt'):],1)
         print "done"         
         combinedGPX = conMngr.combineGPX(originalGPX,newGPX)   
         print "Updating .gpx file ...",
         with open(gpxFilename,'w') as filehandle:
            filehandle.write(combinedGPX)         
         print "done"
         #cleanup
         for guid in new:
            if os.path.exists(guid+".gpx"):
               try:
                  os.remove(guid+".gpx")
               except:
                  print 'Problems removing temporary file %s, aborting deletion.'%(guid+".gpx")
      else:
         gpxPinst.feed('</gpx>',1)
   else:
      print ", but all logs are new.\nYou haven't updated for more than 30 days.\n Please consider downloading a new GPX file.\n No new Caches were loaded."
      gpxPinst.feed('</gpx>',1)

def main(gpxFilename, argv):
   
   # check for command line options
   forceTBupdate = False   
   checkForUpdates = False
   try:
      opts, args = getopt.getopt(argv, "fch", ["forceTBupdate", "checkForUpdates", "help"])
   except getopt.GetoptError:           
      print "Usage: python [-i] <gpx-file> [-forceTBupdate] [-checkForUpdates]"
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-f", "--forceTBupdate"):
         forceTBupdate = True
      elif opt in ('-c', '--checkForUpdates'):
         checkForUpdates = True
      elif opt in ('-h', '--help'):
         print "Usage: python [-i] <gpx-file> [-forceTBupdate] [-checkForUpdates]"
         return(0)
          

   #general configuration
   confParser = ConfigParser({'badgeHTMLfile':'badges.html','proxy':None, 'home':None})
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
      sys.exit(1)
   
   try:
      pers.username = confParser.get('DEFAULT', 'username')
      pers.password = confParser.get('DEFAULT', 'password')
   except:
      print "No username and/or password given in config file"
      sys.exit(1)
   
   if confParser.get('DEFAULT','home'):
      pers.home = [float(a.strip()) for a in confParser.get('DEFAULT','home').split(',')]
   else:
      pers.home = None
   
   badgeHTMLname = confParser.get('DEFAULT', 'badgeHTMLfile')
   
   # value caching (used for coin and TB counts)
   cache = ConfigParser()
   try:
      cache.read('cache.dat')
      if not cache.has_section('TRAVELITEMS'):
         raise Exception()
   except:      
      cache.add_section('TRAVELITEMS')   
      with open('cache.dat', 'wb') as cachefile:
         cache.write(cachefile)
      print "No cache file or no Travelbug section found . A new one was generated."
      cache.read('cache.dat')
   
   # configure connection manager for web spidering
   ConnectionManager.setProxy(confParser.get('DEFAULT', 'proxy'))
   conMngr = ConnectionManager(pers.username, pers.password)
   # set the connection manager to be used for geoTools
   geoTools.net = conMngr
   
   # init the parsers
   gpxPinst = gpxParser(pers)
   badgePinst = badgeParser()
   
   # read the gpx file
   try:
      with open(gpxFilename,'r') as filehandle:
         originalGPX = filehandle.read()
   except:
      print "GPX file '%s' could not be read. Aborting..."%gpxFilename
      raise
   
   print "Parsing caches from gpx ...",
   if checkForUpdates:
      #just leave the closing </gpx> out
      gpxPinst.feed(originalGPX[:-6], 0)
   else:
      gpxPinst.feed(originalGPX, 1)
   print "done"
   
   # check for update
   if checkForUpdates:
      checkUpdates(conMngr, gpxPinst, originalGPX)
      
   ##### BADGE DEFINITION #####
   
   try:
      f = open(badgeHTMLname,'r')
      fc = f.read()
   except:
      f.close()
      print "Badge definition HTML file could not be read from %s"%badgeHTMLname
      fc = conMngr.getBadgeList()
      f = open(badgeHTMLname,'w')
      f.write(fc)
      f.close()
   
   badgePinst.feed(fc)
   badgePinst.close()
   f.close()
   
   # create badges
   print "All: "+str(pers.count)+"  With logs: "+str(pers.logcount)+"  with own logs: "+str(pers.ownlogcount)+"  thereof found: "+str(pers.ownfoundlogcount)
   badgeManager.setCredentials(pers.username, True)
   badgeManager.populate(badgePinst) #creates the standard badges from the website content
   
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
   
   badgeManager.setStatus('Busy',22)
   #badgeManager.setStatus('Busy',10)
   badgeManager.setStatus('Daily',93)
   #badgeManager.setStatus('Daily',4)
   badgeManager.setStatus('Calendar',210)
   #badgeManager.setStatus('Calendar',34)
   badgeManager.setStatus('Scuba',0)
   badgeManager.setStatus('Host',0)
   #badgeManager.setStatus('Distance',18418)
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
      r = conMngr.getCountryList()
      f = open("statelist.txt",'w')
      f.write(r)
      f.close()
   
   badgeManager.setCountryList(r)
   for country in pers.countryList.keys():   
      cBadge = stateBadge(country)
      cBadge.setStatus(len(pers.stateList[country])) 
      badgeManager.addBadge(cBadge)
      
      print 'Visited ' + str(len(pers.stateList[country])) + ' state(s) in ' + country
      print "\t" + str(pers.stateList[country].keys())
   
   ##### GEOGRAPHY #######
   print '\n',
   badgeManager.setStatus('Clouds', pers.hMax)
   print "Found cache above " + str(pers.hMax) + "m N.N."
   badgeManager.setStatus('Gound', pers.hMin)
   print "Found cache below " + str(pers.hMin) + "m N.N."
   badgeManager.setStatus('Distance',pers.maxDistance[1])
   print "Found cache " + str(pers.maxDistance[0])+ " in " + str(pers.maxDistance[1]) + "km distance"
   
   #### COINS ##########
   print '\n',
   # debug version of caching
   # force new downlad by deleting cached file
   if cache.has_option('TRAVELITEMS', 'coins') and cache.has_option('TRAVELITEMS', 'travelbugs') and not forceTBupdate:
            coins = int(cache.get('TRAVELITEMS', 'coins'))
            tbs   = int(cache.get('TRAVELITEMS', 'travelbugs'))         
   else:
      print 'No Coin list cached, retrieving new data ...'
      r = conMngr.getMyCoinList()
      r = re.compile("<script([^>]*)>.*?</script>", re.DOTALL).sub("", r)
      r = re.compile("<span([^>]*)>.*?</span>", re.DOTALL).sub("", r)
      coinP = coinParser()
      coinP.feed(r)
      coins = coinP.CoinCount
      tbs = coinP.TBCount
      cache.set('TRAVELITEMS', 'travelbugs', str(tbs))
      cache.set('TRAVELITEMS', 'coins', str(coins))
      with open('cache.dat', 'ab') as cachefile:
         cache.write(cachefile)
      
   
   badgeManager.setStatus('Coin',coins)
   print "Coins " + str(coins)
   badgeManager.setStatus('Travelbug', tbs)
   print "Travelbugs " + str(tbs)

   outputToHTML(badgeManager, conMngr)
   cleanUp(conMngr)
   
   
def outputToHTML(badgeManager, conMngr):
   #### OUTPUT ##########   
   badgesEarned = badgeManager.getHTML('ALL')   
   text='<center>\n'
   #badges sortet per level
   for level in ['D','E','Sa','R','P','G','S','P']:   
      for t in [b for b in badgesEarned if '%s.png'%level in b or "level=%s"%level in b]:
         text += t
      text += '\n<br/>\n'
   #comments for not generated badges 
   for t in [b for b in badgesEarned if 'generated' in b]:
      text += t
   text += '\n</center>'
   conMngr.saveTemp(text,'badges.html')


def cleanUp(conMngr):
   #Cleanup
   conMngr.cj.save(ignore_discard=True)

# if called directly execute main
if __name__ == "__main__":
    return main(sys.argv[1], sys.argv[2:])