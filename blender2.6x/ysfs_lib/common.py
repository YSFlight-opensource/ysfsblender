# -*- coding: utf-8 -*-

import sys


class Color:
    """Color conversions"""
    def __init__(self, r = 0,  g = 0,  b = 0,  col24 = 0,  brightness = 0): 
        self.r=r
        self.g=g
        self.b=b
        self.col24=col24
        self.brightness = brightness
        
    def calc24b(self):
        self.col24 = self.b/8 + self.r/8*32 + self.g/8*1024
        
    def from24b(self, col24):
        self.col24 = col24
        self.r = 0
        self.g = 0
        self.b = 0
        if col24>1023:
            self.g = col24 / 1024
            col24 -= self.g *1024
        if col24>31:
            self.r = col24 / 32
            col24 -= self.r *32
        self.b = int(col24*255/31.)
        self.g = int(self.g*255/31.)
        self.r = int(self.r*255/31.)
        
    def fromRGB(self, r,  g,  b):
        self.r = r
        self.g = g
        self.b = b
        self.calc24b()
        
    def isEqual2(self,  col):
        return self.r == col.r and self.g == col.g and self.b == col.b and self.col24 == col.col24
        
    def toStr(self): # Print the color
        return str(self.r) +", "+ str(self.g) +", "+ str(self.b) +", "+ str(self.col24) +", "+ str(self.brightness)
        

def nl(): # New Line
    if (sys.platform[:3] == "win") or (sys.platform == "cygwin"):
        return "\n" #the "\r" will be automatically added, else we would get \r\r\n, which is wrong
    else:
        return "\r\n"