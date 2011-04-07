#!python
# -*- coding: UTF-8 -*-

"""Usage: python [-i] <gpx-file> [-f|--forceTBupdate] [-c|--checkForUpdates]

Analyse the given gpx file and retrieve statistics for the geocaches listed.
Retrieve online information for badge definitions, geolocation and elevation 
of caches, trackables found and new geocaches not yet listed in the gpx file.

Command line arguments:
    -f|--forceTBupdate    force an online update of found trackables
    -c|--checkForUpdates  check online for additional founds

General configuration, including username, password, proxy configuration, badge
definition file name and home coordinates are read from a config.cfg file. A 
template is generated if no file is found.

Downloaded informations about elevation, geolocation and trackables are cached 
in the cache.dat file. Use the -f option, delete this file or parts of it to 
force a re-download.

Badge definition is downloaded on first run and saved as .html file 
(path given in config.cfg). Delete this file to force re-download.

Use the -c option to update the loaded .gpx file with the newest finds from 
geocaching.com. Downloaded files are cached for error recovery, but deleted 
after successful integration in .gpx file. !!THE ORIGINAL gpx FILE IS ALTERED!
NO BACKUP IS MADE!!!

Extensive statistics are outputed to console. Generated badges are saved to a
output.html file as a html table.

"""

import sys
import re
import os
import getopt
import time
from calendar import monthrange

from badges import badgeManager, stateBadge
from BadgeParser import BadgeParser
from GpxParser import GpxParser, Pers
from spider import ConnectionManager, savetemp
from geoTools import geoTools
from ConfigParser import SafeConfigParser as ConfigParser
from ConfigParser import NoOptionError
from ProfileParser import CoinParser, OwnParser
from newCacheParser import newCacheParser
from collections import defaultdict
from iso8601 import parse_datetime



def main(gpx_filename, argv):   
    '''Read all sources, parse contents, calculate statistics and badges'''
    
    # Check for command line options.
    force_tb_update = False
    force_owned_update = False
    check_for_updates = False
    try:
        opts, args = getopt.getopt(argv, "toch", ["forceTBupdate",
                                                  "forceOwnUpdate", 
                                                  "checkForUpdates", "help"])
    except getopt.GetoptError:           
        print("Usage: python [-i] <gpx-file> [--forceTBupdate|-t] "
              "[--forceOwnupdate|-o] [--checkForUpdates|-c]")
        sys.exit(2)
    for opt, args in opts:
        if opt in ("-t", "--forceTBupdate"):
            force_tb_update = True
        elif opt in ('-o', '--forceOwnupdate'):
            force_owned_update = True
        elif opt in ('-c', '--checkForUpdates'):
            check_for_updates = True
        elif opt in ('-h', '--help'):
            print("Usage: python [-i] <gpx-file> [-forceTBupdate] "
                  "[-checkForUpdates]")
            return(0)
    # Read in config file.
    conf_parser = prepare_config()
    #prepare caching file
    cache = prepare_caching()
    # Configure connection manager for web spidering.    
    con_mngr_inst = ConnectionManager(Pers.username, Pers.password,
                                      conf_parser.get('DEFAULT', 'proxy'))    
    # Set the connection manager to be used for geoTools.
    geoTools.net = con_mngr_inst   
    # Init the parsers.
    gpx_inst = GpxParser(Pers)
    badgepars_inst = BadgeParser()
    # Read the gpx file.
    start = time.time()
    try:
        with open(gpx_filename,'r') as filehandle:
            originalgpx = filehandle.read()
    except IOError:
        print "gpx file '%s' could not be read. Aborting..."% gpx_filename
        raise
   
    print "Parsing caches from gpx ...",
    if check_for_updates:
        # Just leave the closing </gpx> out.
        gpx_inst.feed(originalgpx[:originalgpx.rfind('</gpx>')], 0)
        savetemp(originalgpx[:-6], 'first.gpx')
    else:
        gpx_inst.feed(originalgpx, 1)
    print "done"
    end = time.time()
    # Check for updates.
    if check_for_updates:
        check_updates(con_mngr_inst, gpx_inst, originalgpx, gpx_filename)
      
    ##### BADGE DEFINITION #####   
    try:
        with open(Pers.badgeHTMLname,'r') as filehandle:
            badgedefinition = filehandle.read()
    except(IOError):        
        print("Badge definition HTML file could not be read from "
              "%s; downloading new copy."%(Pers.badgeHTMLname))
              
        badgedefinition = con_mngr_inst.getbadgelist()
        with open(Pers.badgeHTMLname,'w') as filehandle:
            filehandle.write(badgedefinition)
   
    badgepars_inst.feed(badgedefinition)
    
    print("All: " + str(Pers.count) + "  With logs: " + str(Pers.logcount) +
          "  with own logs: " + str(Pers.ownlogcount) + "  thereof found: " +
          str(Pers.ownfoundlogcount))
    badgeManager.setCredentials(Pers.username, True)
    # Create the standard badges from the website content.
    badgeManager.populate(badgepars_inst) 
    
    create_badges(gpx_inst, con_mngr_inst, cache, force_tb_update, force_owned_update)
    outputhtml()
    cleanup(con_mngr_inst)
    print "Parsing: " + str(end-start)
    return (Pers, gpx_inst, con_mngr_inst, badgepars_inst, badgeManager)

def prepare_config():
    ''' General configuration from conf file'''    
    conf_parser = ConfigParser({'badgeHTMLfile':'badges.html', 'proxy':None, 
                               'home':None})
    if not conf_parser.read('config.cfg'):
        print("No config file found. A new one was generated, please fill in "
              "username and password")
        with open('config.cfg','w') as filehandle:
            filehandle.write('[DEFAULT]\n\n')
            filehandle.write('username = \n')
            filehandle.write('password = \n')
            filehandle.write('badgeHTMLfile = badges.html\n')
            filehandle.write('proxy = None\n')
            filehandle.write('badgeHTMLfile = badges.html\n')
            filehandle.flush() 
        sys.exit(1)
    try:
        Pers.username = conf_parser.get('DEFAULT', 'username')
        Pers.password = conf_parser.get('DEFAULT', 'password')
    except NoOptionError:
        print "No username and/or password given in config file"
        sys.exit(1)
        
    if conf_parser.get('DEFAULT','home'):
        homestring = conf_parser.get('DEFAULT','home')
        Pers.home = [float(a.strip()) for a in homestring.split(',')]
    else:
        Pers.home = None
        
    Pers.badgeHTMLname = conf_parser.get('DEFAULT', 'badgeHTMLfile')
    
    return conf_parser

def prepare_caching():
    ''' Value caching (used for coin and TB counts).'''
    cache = ConfigParser()
    try:
        cache.read('cache.dat')
        if not cache.has_section('TRAVELITEMS'):
            raise KeyError("TRAVELITEMS")
        if not cache.has_section('OWNCACHES'):
            raise KeyError("OWNCACHES")
    except KeyError as e:
        cache.add_section(e.args[0])
        print("No Travelbug/ Own Caches section found . A new one was "
              "generated.")
    except IOError:
        print("No cache file found . A new one was "
              "generated.")
    finally:
        try:
            with open('cache.dat', 'wb') as cachefile:
                cache.write(cachefile)
            cache.read('cache.dat')
        except IOError:
            print "Cachefile could not be written. Continuing without saving."
 
    return cache

def create_badges(gpx_inst, con_mngr, cache_mngr, force_tb_update,
                  force_owned_update):
    ''' Generate the badges from statistical data.
    
    Use the statistical data from the parser runs and the badge definitions to
    create badges and set their status.
    
    '''
    ##### LOGS ####
    if Pers.ownfoundlogcount > 0:
        avgwordcount = Pers.wordcount / Pers.ownfoundlogcount
    else:
        avgwordcount = 0
    print "Average  word count: " + str(avgwordcount)
    badgeManager.setStatus('Author', avgwordcount)
   
    #### OVERALL COUNT #####
    badgeManager.setStatus('Geocacher', Pers.ownfoundlogcount)
    print "Geocaches " + str(Pers.ownfoundlogcount)
   
    ##### TYPES #####
    print '\n'
    types = ['Traditional Cache', 'Multi-cache', 'Unknown Cache', 
             'Letterbox Hybrid', 'Earthcache', 'Wherigo Cache', 
             'CITO Event Cache','Event Cache','Virtual Cache',
             'Mega Social Event Cache','Benchmark','Waymark','Webcam Cache',
             'Project Ape Cache']
   
    for type_ in types:
        generate_type_badges(type_)
    lostn = len([a for a in gpx_inst.all_caches if 'Lost and Found' in a.desc])
    badgeManager.setStatus('Lost', lostn)
    print '10 Years! Cache ' + str(lostn)
    
    ##### CONTAINERS #####
    print '\n',
    types = [u'Not chosen', u'Large', u'Micro', u'Regular', u'Small', u'Other']
    found_types = [a.cache.container for a in gpx_inst.all_caches]
    container_hist = {}
    for con in found_types:
        container_hist[con] = container_hist.get(con,0) + 1
    
    for key in types:
        try:
            badgeManager.setStatus(key[:5], container_hist.get(key,0))
            print key + ' ' + str(container_hist.get(key,0))
        except NameError:
            print key + " No Match"      

    ######### D/T Matrix #############
    print '\n\t',

    dtm = [(float(a.cache.difficulty), float(a.cache.terrain))
           for a in gpx_inst.all_caches]
    matrix = defaultdict(lambda: defaultdict(lambda: 0))
    for pair in dtm:
        matrix[pair[0]][pair[1]] = matrix[pair[0]].get(pair[1],0) + 1
    difficult = terrain = [1.0, 1.5 , 2.0 , 2.5 , 3.0, 3.5, 4.0, 4.5, 5.0]
    mcount = 0
    for dif in difficult:
        for ter in terrain:
            amount = matrix[dif][ter]
            print("%3d" % amount),
            if amount > 0: 
                mcount += 1 
        print "\n\n\t",
    print "Found %d of 81 D/T combinations"% mcount
   
    badgeManager.setStatus('Matrix', mcount)
   
    ####### OTHERS #####
    print '\n',
    try:
        hccs = [wpt.cache for wpt in gpx_inst.all_caches
                if wpt.cache.terrain == u'5' and wpt.cache.difficulty == u'5']
    except AttributeError:
        return gpx_inst.all_caches
    badgeManager.setStatus('Adventur', len(hccs))
    print('HCC Caches: ' + str(len(hccs)) +
          " (" + str([a.name for a in hccs]) + ")")
    
    ftfs = [a.cache for a in gpx_inst.all_caches if 'FTF' in a.cache.logs[0].text]
    badgeManager.setStatus('FTF', len(ftfs))
    print('FTF Caches: ' + str(len(ftfs)) +
          " (" + str([a.name for a in ftfs]) + ")")

    print('\n'),
    if(not force_owned_update):
            try:
                owned = int(cache_mngr.get('OWNCACHES', 'caches_hidden'))
                ownedcaches = cache_mngr.get('OWNCACHES','caches')
                owned_events = int(cache_mngr.get('OWNCACHES', 'owned_events'))
            except NoOptionError:
                print "Cached data incomplete, please redownload with -o"
                owned = 0
                ownedcaches = []
                owned_events = 0
    else:
        print 'No list of hidden caches cached, retrieving new data ...'
        ownlist = con_mngr.get_owner_list()
        ownlist = re.compile("<script([^>]*)>.*?</script>",
                              re.DOTALL).sub("", ownlist)
        ownlist = re.compile("<span([^>]*)>.*?</span>",
                              re.DOTALL).sub("", ownlist)
        ownparser = OwnParser()
        ownparser.feed(ownlist)
        owned = ownparser.owncount
        owned_events = ownparser.own_event_count
        ownedcaches = ownparser.owncaches
        cache_mngr.set('OWNCACHES', 'caches_hidden', str(owned))
        cache_mngr.set('OWNCACHES', 'owned_events', str(owned_events))
        cache_mngr.set('OWNCACHES', 'caches', str(ownedcaches))
        with open('cache.dat', 'ab') as cachefile:
            cache_mngr.write(cachefile)
   
    badgeManager.setStatus('Owner', owned)
    print "Owner of " + str(owned) + ' Caches: ' + str(ownedcaches)

    badgeManager.setStatus('Host', owned_events)
    print "Hosted " + str(owned_events) + ' Events.'
    
    scuba = [a.name for a in gpx_inst.all_caches
             if (5,1) in [(b.id, b.inc) for b in a.cache.attributes]]
    badgeManager.setStatus('Scuba', len(scuba))
    
   
    ##### COUNTRIES #######
    print '\n',
    badgeManager.setStatus('Travelling', len(Pers.countryList))
    print 'Countries traveled ' + str(len(Pers.countryList))
   
    try:
        with open("statelist.txt",'r') as filehandle:
            statelist = filehandle.read()
    except IOError:
        # Couldn't read file, download new.
        try:
            statelist = con_mngr.getcountrylist()
        except Exception:
            # Failed, abort.
            print "Not able to retrieve country list"
            raise
        else:
            # New statelist downloaded, saving for further use.
            try: 
                with open("statelist.txt",'w') as filehandle:
                    filehandle.write(statelist)
            except IOError:
                print("Could not write 'statelist.txt' file.\n"
                      "Continuing without saving")
    if statelist:
        # Only generate with valid statelist, else skip
        badgeManager.setCountryList(statelist)
        for country in Pers.countryList.keys():
            cbadge = stateBadge(country)
            cbadge.setStatus(len(Pers.stateList[country]))
            badgeManager.addBadge(cbadge)      
            print('Visited ' + str(len(Pers.stateList[country])) +
                  ' state(s) in ' + country + "\n\t" + 
                  str(Pers.stateList[country].keys()))
   
    ##### GEOGRAPHY #######
    print('\n'),
    badgeManager.setStatus('Clouds', Pers.hMax)
    print("Found cache above " + str(Pers.hMax) + "m N.N.")
    badgeManager.setStatus('Gound', Pers.hMin)
    print("Found cache below " + str(Pers.hMin) + "m N.N.")
    badgeManager.setStatus('Distance', Pers.max_distance[1])
    print("Found cache " + str(Pers.max_distance[0]) + " in " +
          str(Pers.max_distance[1]) + "km distance")
       
    #### COINS ##########
    print('\n'),
    if(cache_mngr.has_option('TRAVELITEMS', 'coins') and 
       cache_mngr.has_option('TRAVELITEMS', 'travelbugs') and 
       not force_tb_update):
        coins = int(cache_mngr.get('TRAVELITEMS', 'coins'))
        tbs   = int(cache_mngr.get('TRAVELITEMS', 'travelbugs'))
    else:
        print 'No Coin list cached, retrieving new data ...'
        coinlist = con_mngr.getmycoinlist()
        coinlist = re.compile("<script([^>]*)>.*?</script>", 
                              re.DOTALL).sub("", coinlist)
        coinlist = re.compile("<span([^>]*)>.*?</span>", 
                              re.DOTALL).sub("", coinlist)
        coinparser = CoinParser()
        coinparser.feed(coinlist)
        coins = coinparser.CoinCount
        tbs = coinparser.TBCount
        cache_mngr.set('TRAVELITEMS', 'travelbugs', str(tbs))
        cache_mngr.set('TRAVELITEMS', 'coins', str(coins))
        with open('cache.dat', 'wb') as cachefile:
            cache_mngr.write(cachefile)
   
    badgeManager.setStatus('Coin', coins)
    print "Coins " + str(coins)
    badgeManager.setStatus('Travelbug', tbs)
    print "Travelbugs " + str(tbs)
    
    #### DATE ##########
    print('\n'),
    cachebyday = defaultdict(lambda: 0)
    cachebydate = defaultdict(lambda: 0)
    for wpt in gpx_inst.all_caches:
        if 'Z' not in wpt.cache.logs[0].date:
            wpt.cache.logs[0].date += 'Z'
        found = wpt.cache.logs[0].date
        cachebyday[str(parse_datetime(found).date())] += 1
        cachebydate[parse_datetime(found).date().strftime('%m-%d')] += 1
    maxfind = max(cachebyday.values())
    for (key, value) in zip(cachebyday.keys(), cachebyday.values()):
        if value == maxfind:
            maxfinddate = key
    badgeManager.setStatus('Busy', maxfind)
    print("Found %i caches on %s"% (maxfind, maxfinddate))
    badgeManager.setStatus('Calendar', len(cachebydate))
    print("Found caches on %d dates"% (len(cachebydate)))
    days = cachebyday.keys()
    days.sort()
    maxdays = dayscount = 1
    prev = "0000-00-00"
    for date in days:
        if int(date[-2:]) == int(prev[-2:]) + 1:            
            dayscount += 1
        elif (int(date[-2:]) == 1 and 
             int(prev[-2:]) == monthrange(int(prev[:4]) , int(prev[5:7]))[1]):
            dayscount += 1
        else:
            maxdays = max(dayscount, maxdays)
            dayscount = 1
        prev = date
    badgeManager.setStatus('Daily', maxdays)
    print "Found caches on %i consecutive days"% maxdays
    

def generate_type_badges(type_):
    ''' Check if cache type has a badge and set status if yes. '''
    if type_ in Pers.typeCount.keys():
        keys = [key for key in Pers.typeCount.keys()
                    if type_[:5].lower() in key.lower()]
        if len(keys) == 1:
            try:
                badgeManager.setStatus(type_[:5].lower(), 
                                        Pers.typeCount[keys[0]])
                print type_ + ' ' + str(Pers.typeCount[keys[0]])
            except NameError('BadgeName'):
                print("No Match for Cachetype %s found. Nothing was set."%
                        type_)
        elif len(keys) > 1:
            print("Ambiquious type name '" + type_ + "', found (gpx: " + 
                    str(keys) + ") aborting...")
        else: 
            raise LookupError(type_[:5].lower() + " not in badge names.")
    else:
        try:
            badgeManager.setStatus(type_[:5].lower(), 0)
            print type_ + ' ' + str(0)
        except NameError('BadgeName'):
            print("No Match for Cachetype %s found. Nothing was set."% 
                    type_)

def check_updates(con_mngr, gpx_inst, originalgpx, gpx_filename):
    '''Check geocaching.com for caches not yet parsed. Download and Combine.
    
    Use con_mngr to get a recent cache list, compare with parsed list from 
    gpx_inst. Then filter out new ones, parse them and combine into originalgpx
    
    '''
    ncachep_inst = newCacheParser() 
    try:
        # Ask connection manager for an updated list of finds.
        ncachep_inst.feed(con_mngr.getcachelist())
    except Exception:
        print("Couldn't download cache list. Maybe there are connection "
              "problems?\n Continuing without updating.")
        gpx_inst.feed('</gpx>', 1)
        return
    found = [a.url[-36:] for a in gpx_inst.all_caches]
    update = [unicode(b[2]) 
              for b in ncachep_inst.entries 
              if ("Found" in b[0] or "Attended" in b[0])]
    print "Found %d Cache logs online"% len(update),
    new = [b for b in update if b not in found]
    if len(new) < len(found):
        print ", thereof %d were new."% len(new) 
        if new:
            # New will have the newest log first.
            # Reverse it so it's last in the file.
            new.reverse()
            newgpx = []
            for guid in new:
                try:
                    # Ask connection manager for the gpx file of the 
                    # new cache.
                    newgpx.append(con_mngr.getsinglegpx(guid))
                except Exception():
                    print("Couldn't download cache gpx. Maybe there are "
                          "connection problems?\n Aborting the update and "
                          "continuing without.")
                    # Abort parsing, feed closing tag
                    gpx_inst.feed('</gpx>', 1)
                    return
            # Save the position up to where we parsed the original gpx
            parsefrom = originalgpx.rfind('</gpx>')            
            for wpt in newgpx:
                originalgpx = con_mngr.combinegpx(originalgpx, wpt)
            print "Parsing new caches ...",
            gpx_inst.feed(originalgpx[parsefrom:], 1)
            print "done"
            
            print "Updating .gpx file ...",
            with open(gpx_filename, 'w') as filehandle:
                filehandle.write(originalgpx)         
            print "done"
            # Do cleanup
            for guid in new:
                if os.path.exists(guid.strip().upper() + ".gpx"):
                    try:
                        os.remove(guid.strip().upper() + ".gpx")
                    except OSError:
                        print('Problems removing temporary file %s, aborting '
                              'deletion.'%(guid + ".gpx"))
        else:  # No new caches
            gpx_inst.feed('</gpx>', 1)
    else:  # Too many new caches
        print(", but all logs are new. \nYou haven't updated for more than 30 "
              "days.\n Please consider downloading a new gpx file.\n No new "
              "Caches were loaded.")
        gpx_inst.feed('</gpx>', 1)
   
   
def outputhtml():
    '''Output earned badges to HTML file as sorted table.
    
    Retrieves badges from badge_manager and outputs to 'output.html'
    '''
    badges_earned = badgeManager.getHTML('ALL')   
    text = '<center>\n'
    # Badges sorted per level
    for level in ['D', 'E', 'Sa', 'R', 'P', 'G', 'S', 'B']:   
        for badgetext in [b for b in badges_earned if ('%s.png'%level in b or 
                                              "level=%s"%level in b)]:
            text += badgetext
        text += '\n<br/>\n'
    # Vomments for not generated badges 
    for badgetext in [b for b in badges_earned if 'generated' in b]:
        text += badgetext
    text += ('\n<p style="font-size:xx-small">\n----- The Groundspeak'
             ' Geocaching Logo is a registered trademark of '
             '<a href="www.groundpeak.com" >Groundspeak, Inc</a>. Used with '
             'permission. The logo and geocaching.com icons are used with '
             'permission. ----- \n <a href="http://kylemills.net/BadgeGen">'
             'Badges and original GSAK script</a> designed created by '
             'Kyle Mills. -----\n</p>')
    text += '\n</center>'
    try:
        with open('output.html','w') as filehandle:
            filehandle.write(text)
    except(IOError):
        print("Output could not be saved to 'output.html'.")
        raise


def cleanup(con_mngr):
    '''Perform maintenance tasks'''
    con_mngr.cjar.save(ignore_discard=True)


# If called directly, execute main.
if __name__ == "__main__":
    (pers, gpx_inst, con_mngr_inst, 
     badgepars_inst, badge_manager) = main(sys.argv[1], sys.argv[2:])
    c = gpx_inst.all_caches[0]


