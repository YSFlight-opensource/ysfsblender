#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'Select by color'
Blender: 236
Group: 'Mesh'
Tooltip: 'Select all the faces of a given color'
"""



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
widget["color"]  = Draw.Create(0.0,0.0,0.0)


def bevent(evt):
    if evt==2:
        Blender.Window.EditMode(0)
        scn = Blender.Scene.GetCurrent()
        objects = Blender.Object.GetSelected()
        for ob in objects:
            if ob.type == 'Mesh':
                me = ob.getData(mesh=True)
                if me.vertexColors:
##                    print widget["old_color"].val
                    for face in me.faces:
                        cl = face.col[0]
                        if cl.r == int(widget["color"].val[0]*255) and  cl.g == int(widget["color"].val[1]*255) and cl.b == int(widget["color"].val[2]*255):
                            face.sel = 1
        Blender.Window.EditMode(1)
        
def event(evt, val):
    if evt == Draw.ESCKEY:
        Draw.Exit()
        
def gui():
    global widget
    widget["color"] = Draw.ColorPicker(1, 0, 0, 40, 40, widget["color"].val, "Choose the color of the faces you need to select.")
    
    Draw.PushButton("Select", 2, 70, 0, 60, 22, "Replace the old color by the new one.")



Draw.Register(gui, event, bevent)