#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'YS ground objects'
Blender: 236
Group: 'Import'
Tooltip: 'Update the YSFS ground object list (requiered for the .sce importer)'
"""


__author__ = "VincentWeb"
__url__ = ("blender", "",
"Author's homepage, http://shadowhunters.yspilots.com")
__version__ = "0.1"

__bpydoc__ = """\
"""


import sys, os, glob
for path in sys.path:
    if path[-17:] == '/.blender/scripts':
        sys.path.append(path+'/blender')
        
import ysfsConfig
reload(ysfsConfig)
import Blender
from Blender import Registry
        

def update_gro_list():

    gro_objs = {}

    for file in glob.glob(ysfsConfig.ysfs_path+"/ground/[Gg][Rr][Oo]*.lst"):
        
        file = file.replace('\\','/')
        print file
        f=open(file, 'r')
        while 1:
            text=f.readline()
            if text=="":
                break
            while text.find('.dat')==-1:
                text=f.readline()
                if text=="":
                    break
            n_gro=text.split()
            if len(n_gro)>1 and n_gro[0]!="" and n_gro[0]!="\n":
                fileDAT = ysfsConfig.ysfs_path+'/'+n_gro[0]
                fileGRO = ysfsConfig.ysfs_path+'/'+n_gro[1]
                if os.path.exists(fileDAT) and os.path.exists(fileGRO):
                    identify = ""
                    f3 = open(fileDAT, "r")
                    while 1:
                        text2 = f3.readline()
                        if text2 == "":
                            break
                        if len(text2)>8:
                            if text2[:8].upper() == "IDENTIFY":
                                identify = text2[8:].strip().replace('\"','')
                                gro_objs[identify]=fileGRO
                                print "   "+identify
                
                    f3.close()
        f.close()    

    Blender.Registry.SetKey('YSFS_ground_objects', gro_objs, True)

    if len(gro_objs)==0:
        Blender.Draw.PupMenu("No ground objects found, check there is no mistake in the ysfs_path variable of the file ysfsConfig.py")
        Blender.Draw.PupMenu("It's current value is "+ysfsConfig.ysfs_path)
        
if __name__ =='__main__':        
    update_gro_list()