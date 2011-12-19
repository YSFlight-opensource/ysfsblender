#!BPY
# -*- coding: iso-8859-1 -*- 

"""
Name: 'YS DAT Export'
Blender: 236
Group: 'Export'
Tooltip: 'Export hard points, gear position'
"""



__author__ = "VincentWeb"
__url__ = ("blender", "",
"Author's homepage, http://shadowhunters.yspilots.com")
__version__ = "0"

__bpydoc__ = """\
This script exports the hard points
"""

import Blender
import os, sys
from Blender import Window, Scene

def nl(): # New Line
    if (sys.platform[:3] == "win") or (sys.platform == "cygwin"):
        return "\n" #the "\r" will be automatically added, else we would get \r\r\n, which is wrong
    else:
        return "\r\n"

def ff(x):
    n = str(round(x, 2))
    n = n.rstrip('0')
    n = n.rstrip('.')
    if n=="-0":
        n='0'
    return n
    
    
sce = Scene.GetCurrent()
objects = sce.objects
out = file("hardpoints.txt", 'w')
for ob in objects:
    if ob.getType() == 'Empty':
        if ob.name.upper() == "LEFTGEAR":
            s = "LEFTGEAR " + str(ff(-ob.LocY)) + "m " + str(ff(ob.LocZ)) + "m " + str(ff(ob.LocX)) + "m"
            out.write(s+nl())
            print s
        elif ob.name.upper() == "RIGHGEAR" or ob.name.upper() == "RIGHTGEAR":
            s = "RIGHGEAR " + str(ff(-ob.LocY)) + "m " + str(ff(ob.LocZ)) + "m " + str(ff(ob.LocX)) + "m"
            out.write(s+nl())
            print s
        elif ob.name.upper() == "WHELGEAR" or ob.name.upper() == "WHEELGEAR":
            s = "WHELGEAR " + str(ff(-ob.LocY)) + "m " + str(ff(ob.LocZ)) + "m " + str(ff(ob.LocX)) + "m"
            out.write(s+nl())
            print s
        elif ob.name.upper() == "ARRESTER":
            s = "ARRESTER " + str(ff(-ob.LocY)) + "m " + str(ff(ob.LocZ)) + "m " + str(ff(ob.LocX)) + "m"
            out.write(s+nl())
            print s
        elif ob.name.upper() == "MACHNGUN":
            s = "MACHNGUN " + str(ff(-ob.LocY)) + "m " + str(ff(ob.LocZ)) + "m " + str(ff(ob.LocX)) + "m"
            out.write(s+nl())
            print s
        elif ob.name.upper() == "SMOKEGEN":
            s = "SMOKEGEN " + str(ff(-ob.LocY)) + "m " + str(ff(ob.LocZ)) + "m " + str(ff(ob.LocX)) + "m"
            out.write(s+nl())
            print s
        elif ob.name.upper() == "VAPORPO0":
            s = "VAPORPO0 " + str(ff(-ob.LocY)) + "m " + str(ff(ob.LocZ)) + "m " + str(ff(ob.LocX)) + "m"
            out.write(s+nl())
            print s
        elif ob.name.upper() == "VAPORPO1":
            s = "VAPORPO1 " + str(ff(-ob.LocY)) + "m " + str(ff(ob.LocZ)) + "m " + str(ff(ob.LocX)) + "m"
            out.write(s+nl())
            print s
        infos = ob.name.split('_')
        if infos[0] =='HPT':
            s = "HRDPOINT " + str(ff(-ob.LocY)) + "m " + str(ff(ob.LocZ)) + "m " + str(ff(ob.LocX)) + "m " + infos[1]
            out.write(s+nl())
            print s
            
out.close()

Blender.Draw.PupMenu("hardpoints saved in: "+os.getcwd()+"/hardpoints.txt")
