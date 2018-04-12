from math import *  
def calcDistance(Lat_B, Lng_B):  
    EARTH_RADIUS = 6378.137;#km earth equator 
    Lat_A = 0
    Lng_A = 0
    radLat1 = radians(Lat_A)  
    radLat2 = radians(Lat_B)  
    a=radLat1-radLat2  
    b=radians(Lng_A)-radians(Lng_B)  
  
    s = 2 * asin(sqrt(pow(sin(a/2),2)+cos(radLat1)*cos(radLat2)*pow(sin(b/2),2)));    
    s = s * EARTH_RADIUS    
    return s

def calcDistance_two(Lat_A,Lng_A,Lat_B, Lng_B):
    EARTH_RADIUS = 6378.137;#km earth equator 
    radLat1 = radians(Lat_A)  
    radLat2 = radians(Lat_B)  
    a=radLat1-radLat2  
    b=radians(Lng_A)-radians(Lng_B)  
  
    s = 2 * asin(sqrt(pow(sin(a/2),2)+cos(radLat1)*cos(radLat2)*pow(sin(b/2),2)));    
    s = s * EARTH_RADIUS    
    return s