#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'Scenary (.fld)'
Blender: 236
Group: 'Import'
Tooltip: 'Import the objects layout of an YSFlight scenary'
"""


__author__ = "VincentWeb"
__url__ = ("blender", "",
"Author's homepage, http://shadowhunters.yspilots.com")
__version__ = "0.1"

__bpydoc__ = """\
"""


import sys

for path in sys.path:
    if path[-17:] == '/.blender/scripts':
        sys.path.append(path+'/blender')
        

import Blender
import dnm_import
reload(dnm_import)

import update_gro_list
reload(update_gro_list)

from libysfs import *

e = Error()

class GroundObject:
    def __init__(self):
        self.nam = ""
        self.pos = []
        self.id = 0
        self.iff = 0
        self.flg = 0

class FLDReader:
    def __init__(self, gro_objs):
        self.gro_objs = gro_objs # dictionary of ground objects
        self.ground_obj = None
        self.lineNB = 0
        
    def addGroundObject(self, gro):
        print "adding "+gro.nam
        if self.gro_objs.has_key(gro.nam):
            ob = dnm_import.readSRF(self.gro_objs[gro.nam])
            y, z, x, heading,  pitch,  roll = gro.pos
            angles = Angles(-roll, -pitch, heading) # roll = -rotX Blender ; pitch = - rotY Blender ; heading = +rotZ Blender
            angles.YS2Radian()
            ob.LocX = x
            ob.LocY = y
            ob.LocZ = z
            ob.RotX = angles.ax
            ob.RotY = angles.ay
            ob.RotZ = angles.az
            ob.addProperty("NAM", gro.nam, "STRING")
            ob.addProperty("ID", gro.id, "INT")
            ob.addProperty("IFF", gro.iff, "INT")
            ob.addProperty("FLG", gro.flg, "INT")

    def dataFLD(self, data):
        
        if data[0:3].upper() == "GOB":
            self.ground_obj = GroundObject()
            
        if data[0:3].upper() == "POS":
            if self.ground_obj != None:
                pos = data.split()
                try:
                    self.ground_obj.pos = map(float2, pos[1:])
                except:
                    e.outl(self.lineNB,"Impossible to convert to float "+str(pos[1:]))
                
        if data[0:2].upper() == "ID":
            if self.ground_obj != None:
                try: 
                    self.ground_obj.id = int(data[3:4])
                except:
                    e.outl(self.lineNB, "Impossible to convert to int "+data[4:5])
                
        if data[0:3].upper() == "IFF":
            if self.ground_obj != None:
                try: 
                    self.ground_obj.iff = int(data[4:5])
                except:
                    e.outl(self.lineNB, "Impossible to convert to int "+data[4:5])
                
        if data[0:3].upper() == "FLG":
            if self.ground_obj != None:
                try: 
                    self.ground_obj.flg = int(data[4:5])
                except:
                    e.outl(self.lineNB, "Impossible to convert to int "+data[4:5])
                
        if data[0:3].upper() == "NAM":
            if self.ground_obj != None:
                self.ground_obj.nam = data[4:].replace("\n","").strip()
                
        if data[0:3].upper() == "END":
            if self.ground_obj != None:
                self.addGroundObject(self.ground_obj)
                self.ground_obj = None


    def read(self, file):
        f = open(file, "r") 
        while 1:
            line=f.readline()
            self.lineNB +=1
            if line=="":
                break
            self.dataFLD(line)
            
def fs_callback(file):
    gro_objs = Blender.Registry.GetKey('YSFS_ground_objects', True) # True to check on disk also
    if not(gro_objs):
        print "Updating the ground object list."
        update_gro_list.update_gro_list()
        gro_objs = Blender.Registry.GetKey('YSFS_ground_objects', True)
    
    fldReader = FLDReader(gro_objs)
    fldReader.read(file)


if __name__ =='__main__':
    Blender.Window.FileSelector(fs_callback, "Import FLD", "*.fld")
##    fs_callback("/home/vincentweb/maze7.fld")
    print "Scenary imported!"