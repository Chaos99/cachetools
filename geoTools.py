import math

class geoTools():
   @classmethod
   def getState(cls, coords):
      print "Asked to get state for lat " + coords[0] + ", lon " + coords[1]
      return ""
   
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

