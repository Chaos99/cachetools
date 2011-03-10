import math
import urllib2

class geoTools():
   
   net = None
   
   @classmethod
   def getState(cls, (lat,lon)):      
      text = urllib2.urlopen("http://ojw.dev.openstreetmap.org/WhatCountry/?lat=%f&lon=%f"%(lat,lon)).read()
      data = text.strip().split('\n')
      data = [a for a in data if a != '']
      if len(data) == 0:
         ret = ""
      elif data[0] == 'United Kingdom':
         ret = data[2]
      elif len(data) > 1:
         ret = data[1]
      else:
         print "Unusual return value: " + str(data)
         ret = ""
      print "Asked to get state for lat " + str(lat) + ", lon " + str(lon) + "; returning " + ret 
      return ret
   
   @classmethod
   def getDistance(cls, pointA, pointB):      
        # convert from degrees to radians
        latA = math.radians(pointA[0])
        lonA = math.radians(pointA[1])
        latB = math.radians(pointB[0])
        lonB = math.radians(pointB[1])
        #calculate absolute difference for latitude and longitude
        dLat = (latA - latB)
        dLon = (lonA - lonB)
        # do trigonometry magic
        d = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(latA) * math.cos(latB) * math.sin(dLon/2) * math.sin(dLon/2)
        d = 2 * math.asin(math.sqrt(d))
        return (d * 6371)
   
   @classmethod
   def getHeightGeo9(cls, (lat, lon)):
      return int( urllib2.urlopen("http://ws5.geonames.org/srtm3?lat="+str(lat)+"&lng="+str(lon)).read() )
   
   @classmethod
   def getHeightGeo1(cls, (lat, lon)):
      return int( urllib2.urlopen("http://ws5.geonames.org/gtopo30?lat=" + str(lat) + "&lng=" + str(lon)).read() )
   
   @classmethod
   def getHeightGoogle(cls, (lat, lon)):
      text = urllib2.urlopen("http://maps.google.com/maps/api/elevation/xml?locations=" + str(lat) + "," + str(lon) + "&sensor=false").read()
      return float(text.partition("<elevation>")[2].partition("</elevation>")[0])
   
   @classmethod
   def getHeightGeo3(cls, (lat, lon)):
      return int(urllib2.urlopen("http://ws2.geonames.org/astergdem?lat=" + str(lat) + "&lng=" + str(lon)).read() )
   
   @classmethod
   def getHeight(cls, coords):   
         print "Getting elevation for %s" % ( str(coords) )
         source = "default"
         d_Elevation = 0         
         # First try Geonames 30m
         try:
            d_Elevation = cls.getHeightGeo3(coords)
            d_resolution = "30m"
            source = "Geo 30m"
         except:
            d_Elevation = 0
            print "Geo3 failed ..."
         #  If no 30m data and try Geonames 90m resolution       
         if d_Elevation == -9999 or d_Elevation == -32768:        
            try:
               d_Elevation = cls.getHeightGeo9(coords)
               d_resolution = "90m"
               source = "Geo 90m"
            except:
               d_Elevation = 0
               print "Geo9 failed ..."   
         # If no 90m data and try Geonames 1km resolution         
         if d_Elevation == -32768 or d_Elevation == 0:
            try:
               d_Elevation = cls.getHeightGeo1(coords)
               d_resolution = "1km"
               source = "Geo 1km"
            except:
               d_Elevation = 0
               print "Geo1 failed ..."
         # If all else fails then try Google
         if d_Elevation == -9999 or d_Elevation == 0:
            try:
               d_Elevation = cls.getHeightGoogle(coords)
               d_resolution = "90m"
               source = "Google 90m"
            except:
               d_Elevation = 0
               print "Google failed ..."
         # last alternative: geo 30m
         if d_Elevation == 0:
            
                  d_Elevation = 0
         #
         #d_elevation = Round($d_elevation,2)
   
         print "Elevation of %d retrieved for %s from source %s" % (d_Elevation, str(coords), source)
         return d_Elevation