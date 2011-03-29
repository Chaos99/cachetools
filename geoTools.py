import math
import urllib2
import json

class geoTools():
    ''' Retrieve information concerning the geoposition of caches.'''

    net = None

    @classmethod
    def get_state(cls, (lat,lon)):
        #text = urllib2.urlopen("http://ojw.dev.openstreetmap.org/WhatCountry/?lat=%f&lon=%f"%(lat,lon)).read()
        try:
            text = urllib2.urlopen("http://open.mapquestapi.com/nominatim/v1/reverse?format=json&lat=%f&lon=%f"%(lat,lon)).read()
            data = json.loads(text)
            if data['address']['country'] == 'United Kingdom':
                state = data['address']['state_district']
            elif data['address']['country'] == u'\xd6sterreich':
                state = data['address']['state']
            elif data['address']['country'] == 'Danmark':
                state = data['address']['country']
            else:
                print data['address']
                state = data['address']['country']
            ret = state
        except:
            print "Unusual return value: " + str(data)
            ret = ""
        print "Asked to get state for lat " + str(lat) + ", lon " + str(lon) + "; returning " + ret
        return ret

    @classmethod
    def get_distance(cls, pointA, pointB):
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
    def get_height_geo9(cls, (lat, lon)):
        return int( urllib2.urlopen("http://ws5.geonames.org/srtm3?lat="+str(lat)+"&lng="+str(lon)).read() )
    
    @classmethod
    def get_height_geo1(cls, (lat, lon)):
        return int( urllib2.urlopen("http://ws5.geonames.org/gtopo30?lat=" + str(lat) + "&lng=" + str(lon)).read() )
    
    @classmethod
    def get_height_google(cls, (lat, lon)):
        text = urllib2.urlopen("http://maps.google.com/maps/api/elevation/xml?locations=" + str(lat) + "," + str(lon) + "&sensor=false").read()
        return float(text.partition("<elevation>")[2].partition("</elevation>")[0])
    
    @classmethod
    def get_height_geo3(cls, (lat, lon)):
        return int(urllib2.urlopen("http://ws2.geonames.org/astergdem?lat=" + str(lat) + "&lng=" + str(lon)).read() )
    
    @classmethod
    def get_height_osm(cls, (lat, lon)):
        d = json.loads(urllib2.urlopen("http://open.mapquestapi.com/elevation/v1/getElevationProfile?shapeFormat=raw&latLngCollection=%f,%f"%(lat,lon)).read())
        return float(d['elevationProfile'][0]['height'])

    @classmethod
    def get_height(cls, coords):
        print "Getting elevation for %s" % ( str(coords) )
        source = "default"
        d_Elevation = 0
        try:
            d_Elevation = cls.get_height_osm(coords)
            d_resolution = "?m"
            source = "OSM via Mapquest"
        except:
            d_Elevation = 0
            print "OSM failed ..."
        # try Geonames 30m
        if  d_Elevation == 0:
            try:
                d_Elevation = cls.get_height_geo3(coords)
                d_resolution = "30m"
                source = "Geo 30m"
            except:
                d_Elevation = 0
                print "Geo3 failed ..."
        #  If no 30m data and try Geonames 90m resolution
        if d_Elevation == -9999 or d_Elevation == -32768:
            try:
                d_Elevation = cls.get_height_geo9(coords)
                d_resolution = "90m"
                source = "Geo 90m"
            except:
                d_Elevation = 0
                print "Geo9 failed ..."
        # If no 90m data and try Geonames 1km resolution
        if d_Elevation == -32768 or d_Elevation == 0:
            try:
                d_Elevation = cls.get_height_geo1(coords)
                d_resolution = "1km"
                source = "Geo 1km"
            except:
                d_Elevation = 0
                print "Geo1 failed ..."
        # If all else fails then try Google
        if d_Elevation == -9999 or d_Elevation == 0:
            try:
                d_Elevation = cls.get_height_google(coords)
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