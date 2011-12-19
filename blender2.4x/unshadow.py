#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'Unshadow'
Blender: 236
Group: 'Object'
Tooltip: 'Unshadow a mesh'
"""

#FIXME: the script should be in "Mesh" too
#FIXME: do not apply the splitedge modifier twice

__author__ = "VincentWeb"
__url__ = ("blender", "",
"Author's homepage, http://shadowhunters.yspilots.com")
__version__ = "0"


import sys, os
for path in sys.path:
    if path[-17:] == '/.blender/scripts':
        sys.path.append(path+'/blender')

import Blender
from Blender import Draw, BGL
import libysfs
reload(libysfs)

widget = {}
widget["angle"]  = Draw.Create(80.0)


def bevent(evt):
    if evt==2:
        Blender.Window.EditMode(0)
        scn = Blender.Scene.GetCurrent()
        objects = Blender.Object.GetSelected()
        for ob in objects:
            if ob.type == 'Mesh':
                print "unshadow", ob.name
                me = ob.getData(mesh=True)
                edges, faces = libysfs.buildEdgesFacesDics(me)
                libysfs.checkSharpEdges(edges, faces, me, widget["angle"].val)
                mods = ob.modifiers            # get the object's modifiers
                edgesplit_enabled = False
                for mod in mods:
                    if mod.name == "EdgeSplit":
                        mod[Blender.Modifier.Settings.EDGESPLIT_FROM_SHARP] = True
                        mod[Blender.Modifier.Settings.EDGESPLIT_FROM_ANGLE] = False
                        edgesplit_enabled = True
                        break
                if not(edgesplit_enabled):
                    mod = mods.append(Blender.Modifier.Types.EDGESPLIT) 
                    mod[Blender.Modifier.Settings.EDGESPLIT_FROM_SHARP] = True
                    mod[Blender.Modifier.Settings.EDGESPLIT_FROM_ANGLE] = False

        #Blender.Window.EditMode(1)
        
def event(evt, val):
    if evt == Draw.ESCKEY:
        Draw.Exit()
        
def gui():
    global widget
    widget["angle"] = Draw.Number("Min sharp angle", 1, 0, 0, 160, 20, widget["angle"].val, 0, 360, "Minimum angle between two face to consider it is sharp.")
    Draw.PushButton("Unshadow", 2, 162, 0, 70, 20, "Unshadow the selected objects by detecting the sharp edges.")



Draw.Register(gui, event, bevent)