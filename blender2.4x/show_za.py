# SPACEHANDLER.VIEW3D.EVENT

import Blender

def getWindows(type):
    mywindows = []
    windows   = Blender.Window.GetScreenInfo()
    for win in windows:
        if win["type"] == type:
            mywindows.append(win["id"])
    return mywindows

evt = Blender.event
if evt == Blender.Draw.RIGHTMOUSE or evt == Blender.Draw.AKEY or evt == Blender.Draw.BKEY: # or B key selection
    for win in getWindows(Blender.Window.Types["SCRIPT"]):
        Blender.Window.QAdd(win, Blender.Draw.TABKEY, 1, 1)
     # we already entered/exited the object mode
