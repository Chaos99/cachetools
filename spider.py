import urllib2
from urllib import urlencode
import cookielib
import htmlentitydefs
import re
import codecs
import HTMLParser as mHTMLParser
import time
from HTMLParser import HTMLParser
import pickle
import datetime
import os.path
import xml.parsers.expat

class ConnectionManager():
   myurl = ""
   proxyurl = ""
   loginurl = 'http://www.geocaching.com/login/default.aspx'
   searchurl = 'http://www.geocaching.com/seek/nearest.aspx' 
   username = ""
   password = ""
   useragent = "Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3"
   viewstate = ""
   isLoggedIn = False
   cachedFiles = []
      
   def __init__(self):
      self.myurl = urllib2
      proxy = self.myurl.ProxyHandler({'http' : self.proxyurl}) 
      cj = cookielib.LWPCookieJar()  
      opener = self.myurl.build_opener(proxy, urllib2.HTTPCookieProcessor(cj), urllib2.HTTPRedirectHandler())    
      self.myurl.install_opener(opener)
      self.isLoggedIn = False
      self.cachedFiles = []
   ##

   def logon(self):
      """Logs the user in to Geocaching.com."""
      
      # Get the session STATE before requesting the login page
      page = self.myurl.urlopen(self.loginurl)
      m = re.match(r'.+?id="__VIEWSTATE"\s+value="(.+?)"', page.read(), re.S)
      self.viewstate = m.group(1)      
      fromvalues = {  '__VIEWSTATE' : self.viewstate, 'ctl00$ContentBody$myUsername' : self.username, 'ctl00$ContentBody$myPassword' : self.password, 'ctl00_ContentBody_cookie' : 'on', 'ctl00$ContentBody$Button1' : 'Login'}
      headers = { 'User-Agent' : self.useragent }
      fromdata = urlencode(fromvalues)   
      # Login to the site
      request = self.myurl.Request(self.loginurl, fromdata, headers)
      page = self.myurl.urlopen(request)
      inpage =  page.read()
      # Check that logon was successfull      
      if "You are logged in" not in inpage:
         print('cannot logon to the site. '
         'Probably wrong username or password.')
      else:
         print('Successfully logged on to geocaching.com') 
         self.isLoggedIn = True     
   #
   def getMyCoinList(self):
      page = self.myurl.urlopen("http://www.geocaching.com/profile")
      pageC = page.read()
      tempfile = open("temp.html",'w')
      tempfile.write(pageC)
      tempfile.close()
      m = re.match(r'.+?id="__VIEWSTATE"\s+value="(.+?)"', pageC, re.S)
      self.viewstate = m.group(1)
      print "Profile page loaded..."
      fromvalues = {  '__EVENTARGUMENT':'', '__EVENTTARGET':'ctl00$ContentBody$ProfilePanel1$lnkUserStats','__VIEWSTATE' : self.viewstate}
      headers = { 'User-Agent' : self.useragent }
      fromdata = urlencode(fromvalues)
      request = self.myurl.Request(self.searchurl, fromdata, headers)      
      print "Loading Coin page ..."
      try:
         page = self.myurl.urlopen(request)   
      except:
         print "Error while loading page"
      inpage =  page.read()   
      print "... done!"
      #m = re.match(r'.+?id="__VIEWSTATE"\s+value="(.+?)"', inpage, re.S)
      #self.viewstate = m.group(1)       
      return (inpage)
      
  
   
   def getURL(self, text):
      response = self.myurl.urlopen(text)
      index = response.read()
      response.close()
      return index


      

class GeoInfo():
   
   net = None
   
   def __init__(self):
      self.net = ConnectionManager()
   
   def getHeightGeo9(self, lat, lon):
      return int( self.net.getURL("http://ws5.geonames.org/srtm3?lat="+str(lat)+"&lng="+str(lon)))
   ##
   def getHeightGeo1(self, lat, lon):
      return int( self.net.getURL("http://ws5.geonames.org/gtopo30?lat=" + str(lat) + "&lng=" + str(lon)))
   ##
   def getHeightGoogle(self, lat, lon):
      text = self.net.getURL("http://maps.google.com/maps/api/elevation/xml?locations=" + str(lat) + "," + str(lon) + "&sensor=false")
      return float(text.partition("<elevation>")[2].partition("</elevation>")[0])
   ##
   def getHeightGeo3(self, lat, lon):
      return int(self.net.getURL("http://ws2.geonames.org/astergdem?lat=" + str(lat) + "&lng=" + str(lon)))
   ##
   
   def getHeight(self, name, lat, lon):
   
         print "Getting elevation for %s" % ( enc(name) )
         d_Elevation = 0
         
         # First try Geonames 90m
         d_Elevation = self.getHeightGeo9(lat, lon)
         d_resolution = "90m"
         source = "Geo 90m"
   
         # If no 90m data and try Geonames 1km resolution
         if d_Elevation == -32768 or d_Elevation == 0:
                  d_Elevation = self.getHeightGeo1(lat, lon)
                  d_resolution = "1km"
                  source = "Geo 1km"
         # If all else fails then try Google
         if d_Elevation == -9999 or d_Elevation == 0:
                  d_Elevation = self.getHeightGoogle(lat, lon)
                  d_resolution = "90m"
                  source = "Google 90m"
         #
         if d_Elevation == 0:
                  d_Elevation = self.getHeightGeo3(lat, lon)
                  d_resolution = "30m"
                  source = "Geo 30m"
         # 
         if d_Elevation == -9999 or d_Elevation == -32768:
                  d_Elevation = 0
         #
         #d_elevation = Round($d_elevation,2)
   
         print "Elevation of %d retrieved for %s from source %s" % (d_Elevation, enc(name), source)
         return d_Elevation
   ###


