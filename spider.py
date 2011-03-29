''' Holds classes and constants associated with connection to the web.'''
from urllib2 import build_opener, HTTPCookieProcessor, HTTPRedirectHandler
from urllib2 import ProxyHandler, Request, URLError, install_opener, urlopen
from urllib import urlencode
import cookielib
import re
import time
import os.path
import cgi

BASEURL = "http://www.geocaching.com/" 
KYLEURL = 'http://kylemills.net/Geocaching/'
LOGINURL = BASEURL + 'login/default.aspx'
SEARCHURL = BASEURL + 'seek/nearest.aspx'
PROFILURL = BASEURL + 'profile/default.aspx'
BADGEURL = KYLEURL + "BadgeGen/badges.html"
STATELISTURL = KYLEURL + "BadgeGen/badgescripts/statelist.txt"
PRIVATEURL = BASEURL + 'my/'
USERAGENT = ("Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) "
            "AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 "
            "Mobile/1A543 Safari/419.3")
GRACETIME = 5

def savetemp(pagetext, filename='temp.html'):
    ''' General purpose function to save anything to a file.

    Defaults to 'temp.html' if no name given.
    '''
    with open(filename,'w') as filehandle:
        filehandle.write(pagetext)
            
class ConnectionManager():
    ''' Manage internet connection, as well as loading from geocaching.com.'''

    def __init__(self, username, password, proxyurl=None):
        ''' Init instance, use username and password for geocaching.com.'''
        self.cjar = cookielib.LWPCookieJar("cookies.txt")
        try:
            self.cjar.load(ignore_discard = True)
        except(cookielib.LoadError):
            print "No old Cookies loaded, starting new session"
        if proxyurl and proxyurl != 'None':
            proxy = ProxyHandler({'http' : proxyurl})      
            opener = build_opener(proxy, 
                                  HTTPCookieProcessor(self.cjar),
                                  HTTPRedirectHandler())
        else:
            opener = build_opener(HTTPCookieProcessor(self.cjar),
                                  HTTPRedirectHandler()) 
        install_opener(opener)
        self.isloggedin = False
        self.viewstate = ["",""]
        self.username = username
        self.password = password
        self.lastconnection = 0
        self.lastrequest = None
      
    def urlopen(self, request):
        ''' Retrieve contents of given URL.'''
        self.lastrequest = request 
        while time.time() - self.lastconnection < GRACETIME:
            time.sleep(0.5)
        try:
            page = urlopen(request)
            self.cjar.save(ignore_discard = True)
        except (URLError):
            print("Error retrieving %s"% request.get_full_url())
        pagecontent = page.read()
        page.close()
        return pagecontent      

    def logon(self):
        """Logs the user in to Geocaching.com.
        
        Uses cookies to keep connection between sessions.
        Checks established connection before atempting login.
        
        """
        # Get the session STATE before requesting the login page
        pagecontent = self.urlopen(LOGINURL)
        if "You are logged in as" in pagecontent:
            print "Already logged in from previous session"
            self.isloggedin = True
            return
        # Get the session STATE before requesting the login page
        mat = re.match(r'.+?id="__VIEWSTATE"\s+value="(.+?)"', 
                      pagecontent, re.S)
        self.viewstate[0] = mat.group(1)      
        fromvalues = (('__VIEWSTATE', self.viewstate[0]), 
                      ('ctl00$ContentBody$myUsername', self.username), 
                      ('ctl00$ContentBody$myPassword', self.password),
                      ( 'ctl00_ContentBody_cookie', 'on'), 
                      ('ctl00$ContentBody$Button1', 'Login'))
        headers = { 'User-Agent' : USERAGENT }
        fromdata = urlencode(fromvalues)   
        # Login to the site
        request = Request(LOGINURL, fromdata, headers)
        inpage = self.urlopen(request)      
        # Check that logon was successfull      
        if "You are logged in" not in inpage:
            print('cannot logon to the site. '
            'Probably wrong username or password.')
        else:
            print('Successfully logged on to geocaching.com') 
            self.isloggedin = True     
         
    def getmycoinlist(self):
        ''' Retrieve the trackables web page from geocaching.com.'''
        if not self.isloggedin:
            self.logon()
        pagecontent = self.urlopen(PROFILURL) 
        savetemp(pagecontent)
        mat = re.match(r'.+?id="__VIEWSTATE"\s+value="(.+?)"',
                      pagecontent, re.S)
        self.viewstate[0] = mat.group(1)
        print "Profile page loaded..."
        fromvalues = (('__EVENTTARGET', 
                       'ctl00$ContentBody$ProfilePanel1$lnkCollectibles'), 
                      ('__EVENTARGUMENT', ''), 
                      ('__VIEWSTATE', self.viewstate[0]))
        headers = { 'User-Agent' : USERAGENT }
        fromdata = urlencode(fromvalues)      
        request = Request(PROFILURL, fromdata, headers) 
        print("Loading Coin page ..."),
        pagecontent = self.urlopen(request)
        print "... done!"
        #m = re.match(r'.+?id="__VIEWSTATE"\s+value="(.+?)"', inpage, re.S)
        #self.viewstate = m.group(1)
        savetemp(pagecontent,"result.html")
        return (pagecontent) 
   
    def getsinglegpx(self, cid):
        ''' Retrieve a gpx file for a given cache id or guid from gc.com'''
        filename = cid.strip().upper()+".gpx"
        if os.path.exists(filename):
            pagecontent = open(filename,'r').read()
            print "Read cached file for " + cid
            return pagecontent
        else:      
            if not self.isloggedin:
                self.logon()
            if len(cid) < 10:
                cacheurl = BASEURL + 'seek/cache_details.aspx?wp=%s'% cid
            else:
                cacheurl = BASEURL + 'seek/cache_details.aspx?guid=%s'% cid
            pagecontent = self.urlopen(cacheurl)
            mat = re.match(r'.+?id="__VIEWSTATE"\s+value="(.+?)"', 
                          pagecontent, re.S)
            mat2 = re.match(r'.+?id="__VIEWSTATE1"\s+value="(.+?)"', 
                           pagecontent, re.S)
            self.viewstate[0] = mat.group(1)
            self.viewstate[1] = mat2.group(1)
            savetemp(pagecontent, "cache.html")
            print "Cache page %s loaded..."% cid
            fromvalues = (('__EVENTTARGET', ''), 
                          ('__EVENTARGUMENT', ''), 
                          ('__VIEWSTATEFIELDCOUNT', '2'), 
                          ('__VIEWSTATE', self.viewstate[0]),
                          ('__VIEWSTATE1',self.viewstate[1]), 
                          ('ctl00$ContentBody$btnGPXDL','GPX file')) 
            headers = { 'User-Agent' : USERAGENT }
            fromdata = urlencode(fromvalues)      
            request = Request(cacheurl, fromdata, headers) 
            print("Loading GPX file for %s ..."% cid),
            pagecontent = self.urlopen(request)
            print "... done!"
            savetemp(pagecontent, "% s.gpx"% cid.upper())
            return (pagecontent)
      
    def getsinglecache(self, guid):
        ''' Retrieve the print page for a given GUID from gc.com.''' 
        if not self.isloggedin:
            self.logon()
        cacheurl = ("http://www.geocaching.com/seek/cdpf.aspx?guid=%s&lc=5"%
                    guid)
        pagecontent = self.urlopen(cacheurl)      
        savetemp(pagecontent,"Cache.html")
        return pagecontent

    def getcachelist(self):
        ''' Get the last 30 days of logs from personal profile page.'''
        if not self.isloggedin:
            self.logon()
        pagecontent = self.urlopen(PRIVATEURL)      
        #savetemp(pagecontent)      
        print "Private page loaded..."            
        #savetemp(pagecontent,"result.html")
        return (pagecontent) 

    def getcountrylist(self):
        ''' Get the state definition list from kyle mills webpage.''' 
        page = self.urlopen(STATELISTURL)
        return page

    def getbadgelist(self):
        ''' Get the badge definition page from kyle mills webpage.'''
        badgelist = self.urlopen(Request(BADGEURL))
        return badgelist

    def combinegpx(self, first, second):
        '''merge two gpx files (contents), appending second to first'''
        waypoints = []
        #search for <wpt></wpt> pair
        data = re.compile("<wpt([^>]*)>.*?</wpt>", re.DOTALL).search(second)
        while(data):
            if "<name>GC" in data.group(0):
                #discard stages and other non-cache waypoints
                waypoints.append(data.group(0))
            #remove first waypoint, should be the same as matched above
            second = second[second.find("</wpt>")+6:]
            #search for next <wpt></wpt> pair
            data = re.compile("<wpt([^>]*)>.*?</wpt>", re.DOTALL).search(second)
        
        waypoints_clean = []      
        for wpt in waypoints:
            start = wpt[:wpt.find('<groundspeak:logs>')+18]
            end = wpt[wpt.rfind('</groundspeak:logs>'):]
            data = re.compile("<groundspeak:log ([^>]*)>.*?</groundspeak:log>", 
                              re.DOTALL).search(wpt)
            logs_clean = []
            while(data):
                if cgi.escape(self.username) in data.group(0):
                    # Discard foreign logs.
                    logs_clean.append(data.group(0))
                # Remove first log, should be the same as matched above
                wpt = wpt[wpt.find("</groundspeak:log>")+18:]
                #search for next <groundspeak:log></groundspeak:log> pair
                data = re.compile("<groundspeak:log([^>]*)>.*?</groundspeak:log>", 
                                  re.DOTALL).search(wpt)
            logs = ''.join(logs_clean)
            point = start + logs + end
            savetemp(point, 'wpt%s%i'% (second[18:19], len(waypoints_clean)))
            waypoints_clean.append(point)
        
        text = ""
        for wpt in waypoints_clean:
            text += '\n' + wpt
        return first.rstrip()[:-6] + "\n" + text + "\n</gpx>"
