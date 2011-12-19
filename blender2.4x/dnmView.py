#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'DNM View'
Blender: 236
Group: 'Object'
Tooltip: 'Emulate dnmViewer'
"""


__author__ = "VincentWeb"
__url__ = ("blender", "",
"Author's homepage, http://shadowhunters.yspilots.com")
__version__ = "0"

import sys, os
for path in sys.path:
    if path[-17:] == '/.blender/scripts':
        sys.path.append(path+'/blender')
        
from Blender import Draw, BGL
import Blender
import libysfs
reload(libysfs)

import DNMExport
reload(DNMExport)



def display():
    if not(Blender.Window.EditMode()):
        scn = Blender.Scene.GetCurrent()
        ob = scn.objects.active
        print ob.name
        try:
            cla = ob.getProperty("CLA").getData()
        except:
            ob.addProperty("CLA", 0, 'INT')
            cla = 0
##        print cla
        widget["cla_nb"].button.val = cla
        widget["cla_txt"].button.val = cla
        
        ## PRINT pos
        pos = DNMExport.calcPOS(ob)
        updateLocRotField("POS: ", pos)
        
        stas = DNMExport.calcSTA(ob)
        for i in range(min(3,len(stas))):
            pos = stas[i]
            updateLocRotField("STA"+str(i+1)+": ", pos)
        
        print widget["POS:  locx"].button.val, widget["POS:  locy"].button.val, widget["POS:  locz"].button.val
        
        Blender.Draw.Redraw(1)
        
def updateLocRotField(name, pos):
    widget[name+" locx"].button.val = pos[0]
    widget[name+" locy"].button.val = pos[1]
    widget[name+" locz"].button.val = pos[2]
    widget[name+" rotx"].button.val = pos[3]
    widget[name+" roty"].button.val = pos[4]
    widget[name+" rotz"].button.val = pos[5]
    print pos

class Widget:
    def __init__(self, vertx, verty, horx, hory, button):
        self.x = 0
        self.y = 0
        self.vertx = vertx
        self.verty = verty
        self.horx = horx
        self.hory = hory
        self.layout = "vert"
        self.button = button
        self.switch_layout()
        
    def switch_layout(self):
        if self.layout == "vert":
            self.x = self.vertx
            self.y = self.verty
        else:
            self.x = self.horx
            self.y = self.hory
            
widget = {}
widget["vert"] = Widget(0,0,0,0,Draw.Create(0))
widget["hor"] = Widget(70,0,70,0,Draw.Create(1))
widget["cla_nb"] = Widget(160,0,2,45,Draw.Create(0))
widget["cla_txt"] = Widget(245,0,0,25,Draw.Create(0))
            
class LocRotField:
    def __init__(self, event, name, posvert, poshor, visib=False):
        self.name = name
        self.event = event
        self.visib=visib
        self.wname = Widget(posvert.x, posvert.y+44,poshor.x, poshor.y+44, None)
        self.wvisib = Widget(posvert.x+50, posvert.y+44,poshor.x+50, poshor.y+44, Draw.Create(1))
        self.wlocx = Widget(posvert.x, posvert.y+22, poshor.x, poshor.y+22, Draw.Create(0.0))
        self.wlocy = Widget(posvert.x+82, posvert.y+22, poshor.x+82, poshor.y+22, Draw.Create(0.0))
        self.wlocz = Widget(posvert.x+164, posvert.y+22, poshor.x+164, poshor.y+22, Draw.Create(0.0))
        self.wrotx = Widget(posvert.x, posvert.y, poshor.x, poshor.y, Draw.Create(0.0))
        self.wroty = Widget(posvert.x+82, posvert.y, poshor.x+82, poshor.y, Draw.Create(0.0))
        self.wrotz = Widget(posvert.x+164, posvert.y, poshor.x+164, poshor.y, Draw.Create(0.0))
        widget[self.name+" name"]=self.wname
        widget[self.name+" visib"]=self.wvisib
        widget[self.name+" locx"]=self.wlocx
        widget[self.name+" locy"]=self.wlocy
        widget[self.name+" locz"]=self.wlocz
        widget[self.name+" rotx"]=self.wrotx
        widget[self.name+" roty"]=self.wroty
        widget[self.name+" rotz"]=self.wrotz
            
    def gui(self):
        if self.visib:
            Draw.Label(self.name, widget[self.name+" name"].x, widget[self.name+" name"].y, 50, 10) 	
            widget[self.name+" visib"].button = Draw.Toggle("Visible", self.event+2, widget[self.name+" visib"].x, widget[self.name+" visib"].y, 50, 12, widget[self.name+" visib"].button.val, "")
            widget[self.name+" locx"].button = Draw.Number('X: ', self.event+3, widget[self.name+" locx"].x, widget[self.name+" locx"].y, 80, 20, widget[self.name+" locx"].button.val, -1000000000, 1000000000, '', bevent, 0.5, 4)
            widget[self.name+" locy"].button = Draw.Number('Y: ', self.event+3, widget[self.name+" locy"].x, widget[self.name+" locy"].y, 80, 20, widget[self.name+" locy"].button.val, -1000000000, 1000000000, '', bevent, 0.5, 4)
            widget[self.name+" locz"].button = Draw.Number('Z: ', self.event+3, widget[self.name+" locz"].x, widget[self.name+" locz"].y, 80, 20, widget[self.name+" locz"].button.val, -1000000000, 1000000000, '', bevent, 0.5, 4)
            widget[self.name+" rotx"].button = Draw.Number('RotX: ', self.event+3, widget[self.name+" rotx"].x, widget[self.name+" rotx"].y, 80, 20, widget[self.name+" rotx"].button.val, -1000000000, 1000000000, '', bevent, 0.5, 4)
            widget[self.name+" roty"].button = Draw.Number('RotY: ', self.event+3, widget[self.name+" roty"].x, widget[self.name+" roty"].y, 80, 20, widget[self.name+" roty"].button.val, -1000000000, 1000000000, '', bevent, 0.5, 4)
            widget[self.name+" rotz"].button = Draw.Number('RotZ: ', self.event+3, widget[self.name+" rotz"].x, widget[self.name+" rotz"].y, 80, 20, widget[self.name+" rotz"].button.val, -1000000000, 1000000000, '', bevent, 0.5, 4)

pos  = LocRotField(101, "POS: ",  libysfs.Vector(0,30,0), libysfs.Vector(150,0,0), True)#True
sta1 = LocRotField(201, "STA1: ", libysfs.Vector(254,30,0), libysfs.Vector(404,0,0), True)
sta2 = LocRotField(301, "STA2: ", libysfs.Vector(0,100,0), libysfs.Vector(658,0,0), True)
sta3 = LocRotField(401, "STA3: ", libysfs.Vector(254,100,0), libysfs.Vector(912,0,0), True)

locRotFields = [pos, sta1, sta2, sta3]


for w in widget:
    print w

def switch_all_widgets(layout):
    for w in widget:
        widget[w].layout = layout
        widget[w].switch_layout()

def bevent(evt):
    scn = Blender.Scene.GetCurrent()
    ob = scn.objects.active
    if evt == 12:
        widget["cla_nb"].button.val = widget["cla_txt"].button.val
        try:
            ob.removeProperty("CLA")
        except:
            print "no prop"
        ob.addProperty("CLA", widget["cla_txt"].button.val, "INT")
        Draw.Redraw(1)
    elif evt == 11:
        widget["cla_txt"].button.val = widget["cla_nb"].button.val
        try:
            ob.removeProperty("CLA")
        except:
            print "no prop"
        ob.addProperty("CLA", widget["cla_txt"].button.val, "INT")
        Draw.Redraw(1)
    elif evt ==1:
        if widget["vert"].button.val ==1:
            widget["hor"].button.val = 0
            switch_all_widgets("hor")
        else:
            widget["hor"].button.val = 1
            switch_all_widgets("vert")
    elif evt ==2:
        if widget["hor"].button.val ==1:
            widget["vert"].button.val = 0
            switch_all_widgets("vert")
        else:
            widget["vert"].button.val = 1
            switch_all_widgets("hor")
##    print widget["cla_nb"].layout, widget["cla_nb"].x
    Draw.Redraw(1)

def event(evt, val):
    if evt == Draw.ESCKEY:
        Draw.Exit()	
    if evt == Draw.AKEY:
        display()

def gui():
    global widget
    widget["cla_nb"].button = Draw.Number('CLA: ', 11, widget["cla_nb"].x, widget["cla_nb"].y, 80, 20, widget["cla_nb"].button.val, 0, 40, 'the CLA number determine the role of an object.')



    cla_txt_name = ""
    i=0
    for claNB in libysfs.CLA:
        i += 1
        cla_txt_name += libysfs.CLA[claNB].txt+" %x"+str(claNB)+"|"
    widget["cla_txt"].button = Draw.Menu(cla_txt_name, 12, widget["cla_txt"].x, widget["cla_txt"].y, 140, 20, widget["cla_txt"].button.val)

   
    widget["vert"].button = Draw.Toggle("horizontal", 1, widget["vert"].x, widget["vert"].y, 70, 20, widget["vert"].button.val, "Organize those buttons vertically.")
    widget["hor"].button = Draw.Toggle("Vertical", 2, widget["hor"].x, widget["hor"].y, 70, 20, widget["hor"].button.val, "Organize those buttons horizontally.")
    
    for w in locRotFields:
        w.gui()

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
            
loadScriptHandler("show_object.py")

Draw.Register(gui, event, bevent)