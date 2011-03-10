import urllib2
from urllib import urlencode
import cookielib
import htmlentitydefs
import re
import codecs
import time
import os.path


class ConnectionManager():   
   proxyurl = None
   loginurl = 'http://www.geocaching.com/login/default.aspx'
   searchurl = 'http://www.geocaching.com/seek/nearest.aspx'
   profileurl = "http://www.geocaching.com/profile/default.aspx"
   useragent = "Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3"
   

   @classmethod
   def setProxy(cls, proxy):
      if proxy != None and proxy != 'None':
         cls.proxyurl=proxy
      
   def __init__(self,username,password):
      cj = cookielib.LWPCookieJar()
      if self.proxyurl:
         proxy = urllib2.ProxyHandler({'http' : self.proxyurl})      
         opener = urllib2.build_opener(proxy, urllib2.HTTPCookieProcessor(cj), urllib2.HTTPRedirectHandler())
      else:
         opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPRedirectHandler())    
      urllib2.install_opener(opener)
      self.isLoggedIn = False
      self.cachedFiles = []
      self.viewstate = ""
      self.username = username
      self.password = password
      self.graceTime = 3
      self.lastConnection = 0
      self.lastRequest = None
      
   def urlopen(self, request):
      self.lastRequest = request 
      while time.time() - self.lastConnection < self.graceTime:
         sleep(0.5)
      try:
         page = urllib2.urlopen(request)
      except:
         print "Error retrieving %s"%request.get_full_url()
      pageC = page.read()
      page.close()
      return pageC      

   def logon(self):
      """Logs the user in to Geocaching.com."""
      # Get the session STATE before requesting the login page
      pageC = self.urlopen(self.loginurl)
      m = re.match(r'.+?id="__VIEWSTATE"\s+value="(.+?)"', pageC, re.S)
      self.viewstate = m.group(1)      
      fromvalues = (('__VIEWSTATE', self.viewstate), ('ctl00$ContentBody$myUsername', self.username), ('ctl00$ContentBody$myPassword', self.password),( 'ctl00_ContentBody_cookie', 'on'), ('ctl00$ContentBody$Button1', 'Login'))
      headers = { 'User-Agent' : self.useragent }
      fromdata = urlencode(fromvalues)   
      # Login to the site
      request = urllib2.Request(self.loginurl, fromdata, headers)
      inpage = self.urlopen(request)      
      # Check that logon was successfull      
      if "You are logged in" not in inpage:
         print('cannot logon to the site. '
         'Probably wrong username or password.')
      else:
         print('Successfully logged on to geocaching.com') 
         self.isLoggedIn = True     
   #
   def getMyCoinList(self):
      if not self.isLoggedIn:
         self.logon()
      pageC = self.urlopen(self.profileurl)      
      self.saveTemp(pageC)
      m = re.match(r'.+?id="__VIEWSTATE"\s+value="(.+?)"', pageC, re.S)
      self.viewstate = m.group(1)
      print "Profile page loaded..."      
      fromvalues = (('__EVENTTARGET', 'ctl00$ContentBody$ProfilePanel1$lnkCollectibles'), ('__EVENTARGUMENT', ''), ('__VIEWSTATE', self.viewstate))
      headers = { 'User-Agent' : self.useragent }
      fromdata = urlencode(fromvalues)      
      request = urllib2.Request(self.profileurl, fromdata, headers) 
      print "Loading Coin page ..."      
      pageC = self.urlopen(request)
      print "... done!"
      #m = re.match(r'.+?id="__VIEWSTATE"\s+value="(.+?)"', inpage, re.S)
      #self.viewstate = m.group(1)
      self.saveTemp(pageC,"result.html")
      return (pageC)
   
   def getCountryList(self):
      page = self.urlopen('http://kylemills.net/Geocaching/BadgeGen/badgescripts/statelist.txt')
      return page
   
   def saveTemp(self, pagetext, filename='temp.html'):
      tempfile = open(filename,'w')
      tempfile.write(pagetext)
      tempfile.close()