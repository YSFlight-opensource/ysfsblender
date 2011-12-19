#!BPY

# Copyright 2009 Josiah H (Cobra) and Vincent A (Vincentweb)




# FIXME: THE COMPOSITION OF ROTATION ARE WRONG
# FIXME: ZA => rounded + transparency???
# FIXME: objects can have more than 3 STA, see the torch of the stock f1 and the gears
# FIXME: visibility in the POS change nothing? except for objects with STA
# FIXME: 2 objects children of the same empty -> POS pb in the dnm, but when u reload Blender it's fine
# FIXME: scaling a mesh and an object is 2 different process, in the second case, it is made relatively to the midpoint


# TODO: check props, everything should be in POS, not in POS
# TODO: export empty objects of layer 1?
# TODO: if a mesh is used several times, write it only one time
# TODO: Add transparency support
# TODO: Add vertex rounding support
# TODO: Add Graphical User Interface

"""
Name: 'DynaModel (.dnm)...'
Blender: 236
Group: 'Export'
Tooltip: 'Export YSFlight 3D animated object (.dnm)'
"""

__author__ = "Cobra",  "Vincentweb"
__url__ = ["blender", "Vincent's homepage http://shadowhunters.yspilots.com",
"Cobra's homepage, http://joeydrh.googlepages.com"]
__version__ = "0.6"


# For Linux users
import sys
for path in sys.path:
    if path[-17:] == '/.blender/scripts':
        sys.path.append(path+'/blender')

from ysfsConfig import *
#from libysfsExport import *
import libysfsExport
reload(libysfsExport)
from libysfs import *

import math
import Blender
from Blender import sys, Scene, Mesh,  Ipo,  Window
from Blender.Mathutils import *

# useful??
import BPyMesh
import BPyObject
import BPySys
import bpy

e = Error()
print "DNM exporter version "+str(__version__)

editmode = Blender.Window.EditMode()    
if editmode: Blender.Window.EditMode(0) 

def write_numlines(out, mesh):
    numLines = 0
    for vert in mesh.verts:
        numLines += 1
    for face in mesh.faces:
        numLines += 5 
    numLines += 3 # SURF + END + ZA or new line
    out.write('%d' % (numLines))
    out.write(nl())
    
def writeMesh(out, ob):
    out.write('PCK %s ' % (ob.getData(True).replace(' ','_')))
    #write_numlines(out, mesh)
    #we write the SRF part
    buffer = libysfsExport.writeSRF(ob)
    out.write('%d' % (buffer.count("\n")))
    out.write(nl())
    out.write(buffer)
    

def hasAnim(ob):
    """Return 1 if the object has an animation"""
    ipo = ob.getIpo() 
    if ipo == None:
        if 1 in ob.layers:
            # no STA line
            return 0
        else:
            # there is one STA line for the "hide" effect
            return 1
    else:
        # there is an animation
        return 1

def calcPOS(ob):
    """Calculate the POS of an object"""
    emptyParents = []
    ## Fill the emptyParents list
    parent = ob.getParent()
    if parent != None:
        while parent.getType() == "Empty":
            emptyParents.append(parent)
            parent = parent.getParent()
            if parent == None:
                break
##            print "empty parent list", emptyParents            
    pos = [0, 0, 0, 0, 0, 0, 1]
    gotAnim = hasAnim(ob)
    if gotAnim == 1:  
        if len(emptyParents) == 1:
            # The parent of this object is an empty, so POS = coordinates of the empty
            angles = Angles(emptyParents[0].RotZ, -emptyParents[0].RotY, -emptyParents[0].RotX)
            angles.radian2YS()
            pos = [-emptyParents[0].LocY, emptyParents[0].LocZ, emptyParents[0].LocX, angles.ax, angles.ay, angles.az, 1]
#                    print "anim empty parent1"
##                    print "a", emptyParents[0].name, pos
        # if len(emptyParents) == 0 ----------> pos = [0,0,0] = default
        elif len(emptyParents) > 1:
            # The parent of the object is an empty whose parent is an empty, so POS parent1 * parent2*...
            matrix = Blender.Mathutils.Matrix()
            for parent in emptyParents:
                matrix =  matrix * parent.matrixLocal
            euler = matrix.rotationPart().toEuler()
            rotAngle2 = Angles(euler.z, -euler.y, -euler.x)
            rotAngle2.degree2YS()
            trans = matrix.translationPart()
            pos[0] = -trans[1]
            pos[1] = trans[2]
            pos[2] = trans[0]
            pos[3] = rotAngle2.ax
            pos[4] = rotAngle2.ay
            pos[5] = rotAngle2.az
#                    print "anim empty parent >1"
        
    else: 
#                print "no anim"
        # There is no Blender animation. As NST=0, we have to put the coordinates of the object in POS instead of STA
        if len(emptyParents) == 0:
            ##"no empty parent"
            pos = obToPos(ob)
        elif len(emptyParents) >= 1:
            ## "empty parent"
            matrix = ob.matrixLocal
            for parent in emptyParents:
                matrix =  matrix * parent.matrixLocal
            euler = matrix.rotationPart().toEuler()
            rotAngle2 = Angles(euler.z, -euler.y, -euler.x)
            rotAngle2.degree2YS()
            trans = matrix.translationPart()
            pos[0] = -trans[1]
            pos[1] = trans[2]
            pos[2] = trans[0]
            pos[3] = rotAngle2.ax
            pos[4] = rotAngle2.ay
            pos[5] = rotAngle2.az
    return pos

def append2(l, ob, desired_length):
    for i in range(desired_length-len(l)):
        l.append(ob)
        
def copyIpoFrame(list, ipo):
    """Copy in the list 'list' the frame numbers of the ipocurve 'ipo'"""
    for p in ipo:
        list.append(int(p.pt[0]))

def copyIpoPos(list, ipo):
    """Copy in the list 'list' the points of the ipocurve 'ipo'"""
    for p in ipo:
        list.append(p.pt[1])
        
def calcSTA(ob):
    """Caculate the STA lines of the object
    @return: a list of POS list, a POS list is [x,y,z,rotx,roty,rotz,visib]"""
    ipo = ob.getIpo() 
    if ipo == None:
        if 1 in ob.layers:
            return []
        else:
            return [[0,0,0,0,0,0,0]]
    else:
        curveLOCX  = ipo[Ipo.OB_LOCX]
        curveLOCY  = ipo[Ipo.OB_LOCY]
        curveLOCZ  = ipo[Ipo.OB_LOCZ]
        curveROTX  = ipo[Ipo.OB_ROTX]
        curveROTY  = ipo[Ipo.OB_ROTY]
        curveROTZ  = ipo[Ipo.OB_ROTZ]
        curveLAYER = ipo[Ipo.OB_LAYER]

        staX = []
        staY = []
        staZ = []
        staRX = []
        staRY = []
        staRZ = []
        staVis = []
        
        stafX = []
        stafY = []
        stafZ = []
        stafRX = []
        stafRY = []
        stafRZ = []
        stafVis = []
        
        if curveLOCX != None:
            copyIpoPos(staX,curveLOCX.bezierPoints)
            copyIpoFrame(stafX,curveLOCX.bezierPoints)
        if curveLOCY != None:
            copyIpoPos(staY,curveLOCY.bezierPoints)
            copyIpoFrame(stafY,curveLOCY.bezierPoints)
        if curveLOCZ != None:
            copyIpoPos(staZ, curveLOCZ.bezierPoints)
            copyIpoFrame(stafZ, curveLOCZ.bezierPoints)
        if curveROTX != None:
            copyIpoPos(staRX, curveROTX.bezierPoints)
            copyIpoFrame(stafRX, curveROTX.bezierPoints)
        if curveROTY != None:
            copyIpoPos(staRY, curveROTY.bezierPoints)
            copyIpoFrame(stafRY, curveROTY.bezierPoints)
        if curveROTZ != None:
            copyIpoPos(staRZ, curveROTZ.bezierPoints)
            copyIpoFrame(stafRZ, curveROTZ.bezierPoints)
        if curveLAYER != None:
            copyIpoPos(staVis, curveLAYER.bezierPoints)
            copyIpoFrame(stafVis, curveLAYER.bezierPoints)
            
        frames = indexLonger([stafX, stafY, stafZ, stafRX, stafRY, stafRZ, stafVis])
        nst = len(frames)
      
        if 1 in ob.layers:
            layer = 1
        else:
            layer = 2
        append2(staVis,layer,nst)
        
        stas = []

        for i in range(len(frames)):
            Blender.Set("curframe",frames[i])
            pos = obToPos(ob)
            layer = 2
            if int(staVis[i]) == 1: #careful, stavi[i] = 2 ** (layer)
                layer = 1 #so that layer 2 or 3 or ... is set to invisible, and not only layer 2
            visib = -int(layer)+2
##            print visib, staVis[i]
            stas.append([pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], visib])
            
        Blender.Set("curframe",1)
        
    return stas    
        

def write_animations(ob, out):
    stas = calcSTA(ob)
    out.write('NST %d' % (len(stas)))
    out.write(nl())
    for pos in stas:
        out.write('STA %.4f %.4f %.4f %d %d %d %d' % (pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6]))
        out.write(nl())

    
    
def write_dnm(filepath):
    sce = Scene.GetCurrent()
    out = file(filepath, 'w')
    objects = sce.objects
    
    childrenDic = {}
    for ob in objects:
        if (ob.getType() != 'Mesh') and (ob.getType() != 'Empty'): 
                pass
        else:
            childrenDic[ob.name] = []

    
    out.write('DYNAMODEL'+nl()) # Begin with the tag "DYNAMODEL" to show that this is a valid DNM file
    out.write('DNMVER 1'+nl())
#    out.write('\r\n'+nl())
    
    ipos = dict()

    objectNb = 0
    # We take an inventory of all the meshes in meshDic to avoid writting them several times
    meshDic = {}
    for ob in objects:
        if ob.getType() == 'Mesh':
            meshDic[ob.getData(True)] = False #ob.getData(True) return the name of the mesh linked with the object ob
            
    for ob in objects:
        objectNb += 1
        if (ob.getType() != 'Mesh'): 
                pass
        else:
            parent = ob.getParent()
            if  parent == None:
                pass
            else:
                while parent.getType() == "Empty":
                    parent = parent.getParent()
                    if parent == None:
                        break
                if parent != None:        
                    childrenDic[parent.name].append(ob.name) # build the children dictionary
            if ob.getType() == 'Mesh':
                mesh = ob.getData(mesh=1)
                Window.DrawProgressBar (float(objectNb)/len(objects), "Exporting "+ob.name)
                print ob.name
                if not(meshDic[ob.getData(True)]):
                    writeMesh(out,ob)
                    meshDic[ob.getData(True)] = True
                    
            
    for ob in objects:
        if (ob.getType()!='Mesh'):
                pass
        else:
            mesh = ob.getData(mesh=1)
            out.write('SRF "%s"' % (ob.getName()))
            out.write(nl())
            out.write('FIL %s' % (ob.getData(True).replace(' ','_')))
            out.write(nl())
            try:
                out.write('CLA %d' % (ob.getProperty("CLA").getData()))
                out.write(nl())
            except:
                out.write('CLA 0'+nl())
                
            write_animations(ob, out)
            
            pos = calcPOS(ob)
                
            out.write('POS %.4f %.4f %.4f %d %d %d %d' % (pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6]))
            out.write(nl())
            out.write('CNT 0.00 0.00 0.00'+nl())
            out.write('REL DEP'+nl())
            out.write('NCH %d' % (len(childrenDic[ob.name])))
            out.write(nl())
            for child in childrenDic[ob.name]:
                out.write('CLD "%s"' % (child))
                out.write(nl())
                
            
                
            out.write('END'+nl())
    
    out.write('END'+nl())
    out.close()
    
def fs_callback(filename):
    Window.DrawProgressBar (0.0, "Exporting the dnm...")
    Window.WaitCursor(1)
    write_dnm(filename)
    Window.WaitCursor(0)
    Window.DrawProgressBar (1.0, "Finished") 
    if e.errorNB > 0:
            Blender.Draw.PupMenu( "Check the console, there are "+str(e.errorNB)+" errors.")
    print "Exported"


if __name__ =='__main__':
    Blender.Window.FileSelector(fs_callback, "Export a .dnm model",   Blender.sys.makename(ext='.dnm'))
#write_dnm("/home/vincentweb/ysflight/aircraft/f16.dnm")

