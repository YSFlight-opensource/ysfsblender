#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'Replace a color'
Blender: 236
Group: 'Mesh'
Tooltip: 'Replace a color'
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
widget["old_color"]  = Draw.Create(0.0,0.0,0.0)
widget["new_color"]  = Draw.Create(1.0,1.0,1.0)


def bevent(evt):
    if evt==3:
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
                        if cl.r == int(widget["old_color"].val[0]*255) and  cl.g == int(widget["old_color"].val[1]*255) and cl.b == int(widget["old_color"].val[2]*255):
                            for col in face.col:
                                col.r = int(widget["new_color"].val[0]*255)
                                col.g = int(widget["new_color"].val[1]*255)
                                col.b = int(widget["new_color"].val[2]*255)
        Blender.Window.EditMode(1)
        
def event(evt, val):
    if evt == Draw.ESCKEY:
        Draw.Exit()
        
def gui():
    global widget
    widget["old_color"] = Draw.ColorPicker(1, 0, 0, 40, 40, widget["old_color"].val, "Choose the old color to replace.")
    Draw.Label(" -> ", 40, 13, 40, 15)
    widget["new_color"] = Draw.ColorPicker(2, 70, 0, 40, 40, widget["new_color"].val, "Choose the new color which will replace the new one.")
    Draw.PushButton("Replace", 3, 120, 0, 60, 22, "Replace the old color by the new one.")



Draw.Register(gui, event, bevent)