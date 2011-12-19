#!BPY

"""
Name: 'Surf (.srf)...'
Blender: 236
Group: 'Export'
Tooltip: 'Export YSFlight 3D format (.srf)'
"""

__author__ = "Cobra",  "Vincentweb"
__url__ = ["blender", "Vincent's homepage http://shadowhunters.yspilots.com",
"Author's homepage, http://joeydrh.googlepages.com"]
__version__ = "0.9"


# Copyright 2009 Josiah H (Cobra) and Vincent A (Vincentweb)
# Script started by Josiah H (Cobra) and revised by Vincent A (Vincentweb)


## Changes ##
#- scaling was applied after rotation which conducted to problems
#- apply tranlations and rotations to normals and face midpoints



# TODO: optimize file size: -0  -> 0      1.60000 -> 1.6
# TODO: Add transparency support
# TODO: Add Graphical User Interface like the DirectX exporter

# For Linux users
import sys
for path in sys.path:
    if path[-17:] == '/.blender/scripts':
        sys.path.append(path+'/blender')

import os,  time
#from libysfsExport import *
from libysfs import *
import libysfsExport,  Blender
reload(libysfsExport)

#------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------


def write_obj(filepath):
    editmode = Blender.Window.EditMode()    
    if editmode: Blender.Window.EditMode(0) 

    time1 = time.time()
    print "Exporting a YSFlight object..."
    
    out = file(filepath, 'w')
#    sce = bpy.data.scenes.active
    sce = Blender.Scene.GetCurrent()
    
    if exportMode == 0:
        print "Mode export last object"
        objects = sce.objects
        for ob in objects:
            if ob.getType()!='Mesh': 
                pass
            else:
                out.write(libysfsExport.writeSRF(ob, True))
                out.close()
                break
    elif exportMode == 1:
        print "Mode export all objects into different files"
        dir = os.path.dirname(filepath)  #We ignore the filepath written by the user, but we use it to get the directory
        objects = sce.objects
        for ob in objects:
            if ob.getType()!='Mesh': 
                pass
            else:
                out = file(ob.name+".srf", 'w')
                out.write(libysfsExport.writeSRF(ob, True))
                out.close()
    else:
        print "Mode export selected object"
        if len(Blender.Object.GetSelected()) > 0:
            ob = Blender.Object.GetSelected()[0] 
            if ob.getType()!='Mesh': 
                pass
            else:
                out.write(libysfsExport.writeSRF(ob, True))
                out.close()
        else:
            pass
    print "SRF Export time: %.2f seconds" % (time.time() - time1)


Blender.Window.FileSelector(write_obj, "Export a .srf model",  Blender.sys.makename(ext='.srf'))
#write_obj("/home/vincentweb/__.srf")
