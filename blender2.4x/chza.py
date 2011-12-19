#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'YS Face mode'
Blender: 236
Group: 'Mesh'
Tooltip: 'Change the mode - transparency (ZA, ZL), brightness... - of the selected faces.'
"""

#TODO: the button "install" should diseappear once the 2 other scripts are registered in the space handler

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

zatex = libysfs.Ztex("za")
##zztex = libysfs.Ztex("zz")

if not(zatex.success):
    Blender.Draw.PupMenu("Failed to load some ZA textures, see the console.")
##if not(zztex.success):
##    Blender.Draw.PupMenu("Failed to load some ZZ textures, see the console.")

#TODO: ZA -> smooth???
#TODO: don't load the texture twice!!!
#TODO: ZA from 0-255? 256?


        
widget = {}
widget["color"]      = Draw.Create(1.0,1.0,1.0)
widget["ZA_toggle"]  = Draw.Create(0)
widget["ZA_number"]  = Draw.Create(0)
widget["ZZ_toggle"]  = Draw.Create(0)
##widget["ZZ_number"]  = Draw.Create(0)
widget["ZL_toggle"]  = Draw.Create(0)
widget["BR_toggle"]  = Draw.Create(0)
widget["DS_toggle"]  = Draw.Create(0)
widget["SV_toggle"]  = Draw.Create(0)
widget["SF_toggle"]  = Draw.Create(0)
widget["SZA_toggle"] = Draw.Create(0)
widget["SZZ_toggle"] = Draw.Create(0)
widget["SBR_toggle"] = Draw.Create(0)
widget["lim_number"] = Draw.Create(100)

Blender.Registry.SetKey('Z_widget', widget, True)


import Blender
from Blender import Draw
evt = Blender.event

def display():
    if Blender.Window.EditMode(): #else we are in object mode, useless
        Blender.Window.EditMode(0)
        scn = Blender.Scene.GetCurrent()
        ob = scn.objects.active
        if ob.type == 'Mesh':
            me = ob.getData(mesh=True)
            for face in me.faces:
                if face.sel:
                    if me.vertexColors:
##                    print widget["old_color"].val
                        widget["color"].val = (face.col[0].r/255., face.col[0].g/255., face.col[0].b/255.)
                    else:
                        widget["color"].val = (1.0,1.0,1.0)
    ##                print face.index
                    if me.faceUV:                     
                        if face.transp ==2:
                            if face.image == None:
                                widget["ZA_number"].val = 128
                                widget["ZA_toggle"].val = 1
                                widget["ZZ_toggle"].val = 0
##                                widget["ZZ_number"].val = 0
                            elif face.image.name[0:2]=="za":
                                widget["ZA_toggle"].val = 1
                                widget["ZA_number"].val = int(face.image.name[2:-4].replace(".png", ""))
##                                widget["ZZ_toggle"].val = 0
##                                widget["ZZ_number"].val = 0
                            elif face.image.name[0:2]=="zz":
                                widget["ZZ_toggle"].val = 1
##                                widget["ZZ_number"].val = int(face.image.name[2:-4].replace(".png", ""))
##                                widget["ZA_toggle"].val = 0
##                                widget["ZA_number"].val = 0
                            else:
                                widget["ZA_number"].val = 128
                                widget["ZA_toggle"].val = 1
                                widget["ZZ_toggle"].val = 0
##                                widget["ZZ_number"].val = 0
                        else:
                            widget["ZA_toggle"].val = 0
                            widget["ZA_number"].val = 0
                            widget["ZZ_toggle"].val = 0
##                            widget["ZZ_number"].val = 0         

                        b = str(libysfs.binary(face.mode))
                        b = b[::-1] # reverse b
                        
                        if len(b)>8 and b[8]=='1':
                            widget["ZL_toggle"].val = 1
                        else:
                            widget["ZL_toggle"].val = 0
                        if len(b)>4 and b[4]=='1':
                            widget["BR_toggle"].val = 1
                        else:
                            widget["BR_toggle"].val = 0
                        if len(b)>9 and b[9]=='1':
                            widget["DS_toggle"].val = 1
                        else:
                            widget["DS_toggle"].val = 0
                                
                                
                    else:
                        widget["ZA_toggle"].val = 0
                        widget["ZA_number"].val = 0
                        widget["ZZ_toggle"].val = 0
##                        widget["ZZ_number"].val = 0
                        widget["ZL_toggle"].val = 0
                        widget["BR_toggle"].val = 0
                        widget["DS_toggle"].val = 0
                    break
        Blender.Draw.Redraw(1)   
        Blender.Window.EditMode(1)

def bevent(evt):
    global zatex
    if evt%10==2 or evt%10==1 or evt%10==3:
        Blender.Window.EditMode(0)
        
        scn = Blender.Scene.GetCurrent()
        ob = scn.objects.active
        if ob.type == 'Mesh':
            me = ob.getData(mesh=True)
            for face in me.faces:
                if face.sel:
##                    print face.index
                    if evt == 2:
                        widget["ZA_toggle"].val = 1
                        me.faceUV = True
                        face.mode|=Blender.Mesh.FaceModes['TEX'] 
                        face.transp|=Blender.Mesh.FaceTranspModes['ALPHA']
                        if zatex.hasimage[widget["ZA_number"].val]:
                            face.image = zatex.image[widget["ZA_number"].val]
                        else:
                            print "Cannot set the ZA value, I failed to load the texture."
                            Blender.Draw.PupMenu("Cannot set the ZA value, I failed to load the texture.")
        
                    elif evt == 12:
                        widget["ZZ_toggle"].val = 1
                        me.faceUV = True
                        face.mode|=Blender.NMesh.FaceModes['TEX'] 
                        face.transp|=Blender.NMesh.FaceTranspModes['BILLBOARD']
##                        if zatex.hasimage[widget["ZZ_number"].val]:
##                            face.image = zztex.image[widget["ZZ_number"].val]
##                        else:
##                            print "Cannot set the ZZ value, I failed to load the texture."
##                            Blender.Draw.PupMenu("Cannot set the ZZ value, I failed to load the texture.")
                    
                    elif evt == 1:
                        if widget["ZA_toggle"].val ==1:
##                            widget["ZZ_toggle"].val =0
                            me.faceUV = True
                            face.mode|=Blender.Mesh.FaceModes['TEX'] 
                            face.transp|=Blender.Mesh.FaceTranspModes['ALPHA']
                            if zatex.hasimage[widget["ZA_number"].val]:
                                face.image = zatex.image[widget["ZA_number"].val]
                            else:
                                print "Cannot set the ZA value, I failed to load the texture."
                                Blender.Draw.PupMenu("Cannot set the ZA value, I failed to load the texture.")
                        else:
                            if me.faceUV:
                                face.mode&=~Blender.Mesh.FaceTranspModes['ALPHA']
##                                face.mode&=~Blender.Mesh.FaceModes['TEX']
                                
                    elif evt == 11:
                        if widget["ZZ_toggle"].val ==1:
##                            widget["ZA_toggle"].val =0
                            me.faceUV = True
                            face.mode|=Blender.Mesh.FaceModes['BILLBOARD'] 
##                            face.transp|=Blender.Mesh.FaceTranspModes['ALPHA']
##                            if zatex.hasimage[widget["ZZ_number"].val]:
##                                face.image = zatex.image[widget["ZZ_number"].val]
##                            else:
##                                print "Cannot set the Z value, I failed to load the texture."
##                                Blender.Draw.PupMenu("Cannot set the ZZ value, I failed to load the texture.")
                        else:
                            if me.faceUV:
                                face.mode&=~Blender.Mesh.FaceModes['BILLBOARD']
##                                face.mode&=~Blender.Mesh.FaceModes['TEX']
                        
                    elif evt == 23:
                        if widget["ZL_toggle"].val ==1:
                            me.faceUV = True
                            face.mode|=Blender.Mesh.FaceModes['HALO']
                        else:
                            if me.faceUV:
                                face.mode&=~Blender.Mesh.FaceModes['HALO']
                    
                    elif evt == 33:
                        if widget["BR_toggle"].val ==1:
                            me.faceUV = True
                            face.mode|=Blender.Mesh.FaceModes['LIGHT']
                        else:
                            if me.faceUV:
                                face.mode&=~Blender.Mesh.FaceModes['LIGHT']
                                
                    elif evt == 43:
                        if widget["DS_toggle"].val ==1:
                            me.faceUV = True
                            face.mode|=Blender.Mesh.FaceModes['TWOSIDE']
                        else:
                            if me.faceUV:
                                face.mode&=~Blender.Mesh.FaceModes['TWOSIDE']
                                
                    elif evt == 63 or evt==64:
                        me.vertexColors = True
                        for col in face.col:
                            col.r = int(widget["color"].val[0]*255)
                            col.g = int(widget["color"].val[1]*255)
                            col.b = int(widget["color"].val[2]*255)
        Blender.Draw.Redraw(1)               
        Blender.Window.EditMode(1)
        
    elif evt == 4:   
        display()
        
    elif evt == 60:
        Blender.Draw.PupMenu("To display the vertices, face, ... IDs or")
        Blender.Draw.PupMenu("To display the face mode of the selecting face without having to press the Display button, follow the instructions below:")
        Blender.Draw.PupMenu("In the menu of the 3D-view window, click on 'View', got to 'Space Handler Scripts'.")
        Blender.Draw.PupMenu("Then enable the script 'Event: YS auto Face mode' and 'Draw: show_id.py'")



def event(evt, val):
    if evt == Draw.ESCKEY:
        Draw.Exit()
    elif evt == Draw.TABKEY:
        display()


def gui():
    global widget
    widget["ZA_toggle"] = Draw.Toggle("ZA", 1, 0, 0, 30, 20, widget["ZA_toggle"].val, "use ZA (transparency) on this face")
    widget["ZA_number"] = Draw.Number('ZA: ', 2, 30,0, 75, 20, widget["ZA_number"].val, 0,255, 'Transparency level, the face(s) will appear solid for non-openGL users.')
##    Draw.PushButton("Apply", 3, 105, 0, 50, 20)
    
    widget["ZZ_toggle"] = Draw.Toggle("ZZ", 11, 0, 22, 30, 20, widget["ZZ_toggle"].val, "use ZZ (transparency) on this face")
##    widget["ZZ_number"] = Draw.Number('ZZ: ', 12, 30, 22, 75, 20, widget["ZZ_number"].val, 0,255, 'Transparency level, the face(s) will be invisible for non-openGL users.')
##    Draw.PushButton("Apply", 13, 105, 22, 50, 20)

    widget["ZL_toggle"] = Draw.Toggle("ZL", 23, 0, 44, 105, 20, widget["ZL_toggle"].val, "use ZL, add a dot on the midpoint of this face, used for light.")
    
    widget["BR_toggle"] = Draw.Toggle("Bright", 33, 0, 66, 105, 20, widget["BR_toggle"].val, "Render this face bright.")
    
    widget["DS_toggle"] = Draw.Toggle("Double sided", 43, 0, 88, 105, 20, widget["DS_toggle"].val, "This face is double sided, ie can be viewed from both sided (it's normal is the vector (0 ; 0 ; 0)).")

    Draw.PushButton("Display", 4, 0, 152, 52, 20, "Display the modes of the selected face (or of the first of all the selected faces). If you are annoyed to press this button, press the Install button.")
    Draw.PushButton("Install", 60, 53, 152, 52, 20, "I guess you are annoyed to press the Display button!")
    
    widget["color"] = Draw.ColorPicker(63, 1, 112, 50, 30, widget["color"].val, "Choose the color to set to the selected faces.")
    Draw.PushButton("Set", 64, 52, 112, 52, 20, "Change the color to the selected faces")
    
    widget["lim_number"] = Draw.Number('max: ', 22, 120, 0, 80, 20, widget["lim_number"].val, 1,1000, 'Maximum of ID to display, high values may freeze Blender.')
    widget["SV_toggle"] = Draw.Toggle("Show vert ID", 21, 120, 22, 80, 20, widget["SV_toggle"].val, "Display the vertex ID of the selected vertices in the 3D-View Window.")    
    widget["SF_toggle"] = Draw.Toggle("Show face ID", 31, 120, 44, 80, 20, widget["SF_toggle"].val, "Display the face ID of the selected faces in the 3D-View Window.")
    widget["SZA_toggle"] = Draw.Toggle("Show ZA", 41, 120, 66, 80, 20, widget["SZA_toggle"].val, "Display the ZA value of the selected faces in the 3D-View Window.")
    widget["SZZ_toggle"] = Draw.Toggle("Show ZZ", 51, 120, 88, 80, 20, widget["SZZ_toggle"].val, "Display the ZZ value of the selected faces in the 3D-View Window.")
    widget["SBR_toggle"] = Draw.Toggle("Show bright", 61, 120, 112, 80, 20, widget["SBR_toggle"].val, "Display in the 3D-View Window if the selected faces are bright.")
    

def loadScriptHandler(script):
    try:
        Blender.Text.unlink(Blender.Text.Get(script))
        # To avoid loading twiwe the same text and having plenty of script handlers
    except:
        print "first start!!!"
    try:
        txt = Blender.Text.Load(Blender.Get('scriptsdir')+"/blender/"+script)
    except:
        try:
            txt = Blender.Text.Load(Blender.Get('scriptsdir')+"/"+script)
        except:
            Blender.Draw.PupMenu("Failed to load "+script+" It is neither in "+Blender.Get('scriptsdir')+" neither in "+Blender.Get('scriptsdir')+"/blender")  
            
loadScriptHandler("show_za.py")
loadScriptHandler("show_id.py")

Draw.Register(gui, event, bevent)
