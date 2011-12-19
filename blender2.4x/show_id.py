# SPACEHANDLER.VIEW3D.DRAW

# Credits to Crouch for the major part of this script - http://sites.google.com/site/bartiuscrouch/snippets

import threading
import Blender

import sys
for path in sys.path:
    if path[-17:] == '/.blender/scripts':
        sys.path.append(path+'/blender')

import libysfs
reload(libysfs)

def drawText(drawlist, colour, decal=0):
    viewMatrix = Blender.Window.GetPerspMatrix()
    viewBuff = [viewMatrix[i][j] for i in xrange(4) for j in xrange(4)]
    viewBuff = Blender.BGL.Buffer(Blender.BGL.GL_FLOAT, 16, viewBuff)
    Blender.BGL.glLoadIdentity()
    Blender.BGL.glMatrixMode(Blender.BGL.GL_PROJECTION)
    Blender.BGL.glLoadMatrixf(viewBuff)
    Blender.BGL.glColor3f(colour[0], colour[1], colour[2])
    
    for info in drawlist:
        loc, text = info
        Blender.BGL.glRasterPos3f(loc[0], loc[1]+decal, loc[2])
        Blender.Draw.Text(text)

def drawVerts(verts, matrix):
    drawlist = []
    colour = [1.0, 1.0, 0.0]
    for v in verts:
        drawlist.append([v.co*matrix, str(v.index)])
    drawText(drawlist, colour)

def drawFaces(faces, matrix):
    drawlist = []
    colour = [1.0, 0.0, 1.0]
    for f in faces:
        drawlist.append([f.cent*matrix, str(f.index)])
    drawText(drawlist, colour)
    
def drawFacesBR(me, faces, matrix):
    drawlist = []
    colour = [0.0, 1.0, 0.0]
    if me.faceUV:
        for f in faces:
            b = str(libysfs.binary(f.mode))
            b = b[::-1] # reverse b
            if len(b)>4 and b[4]=='1':
                drawlist.append([f.cent*matrix, "   B"])
    drawText(drawlist, colour)
    
def drawFacesZA(me, faces, matrix):
    drawlist = []
    colour = [1.0, 1.0, 1.0]
    if me.faceUV:
        for f in faces:
            if f.transp ==2:
                if f.image == None:
                    drawlist.append([f.cent*matrix, "ZA "+128])
                elif f.image.name[0:2]=="za":
                    drawlist.append([f.cent*matrix, "ZA "+f.image.name[2:-4].replace(".png", "")])
    drawText(drawlist, colour, 0.15)
    
def drawFacesZZ(me, faces, matrix):
    drawlist = []
    colour = [0.0, 0.0, 0.0]
    if me.faceUV:
        for f in faces:
            b = str(libysfs.binary(f.mode))
            b = b[::-1] # reverse b
            if len(b)>12 and b[12]=='1':
                drawlist.append([f.cent*matrix, "ZZ"])
    drawText(drawlist, colour, 0.15)

# we already entered/exited the object mode
try:
    widget = Blender.Registry.GetKey('Z_widget', True)
except:
    print "YS Face ID doesn't seem to be launched :("
else:
    if widget["SV_toggle"].val == 1:    
        scn = Blender.Scene.GetCurrent()
        ob = scn.objects.active
        if ob.type == 'Mesh':
            me = ob.getData(mesh=True)
            verts = []
            for vert in me.verts:
                if len(verts) <  widget["lim_number"].val:
                    if vert.sel:
                        verts.append(vert)
                else:
                    break
            drawVerts(verts, ob.matrix)
            
    if widget["SF_toggle"].val == 1:    
        scn = Blender.Scene.GetCurrent()
        ob = scn.objects.active
        if ob.type == 'Mesh':
            me = ob.getData(mesh=True)
            faces = []
            for face in me.faces:
                if len(faces) <  widget["lim_number"].val:
                    if face.sel:
                        faces.append(face)
                else:
                    break
            drawFaces(faces, ob.matrix)
            
    if widget["SBR_toggle"].val == 1:    
        scn = Blender.Scene.GetCurrent()
        ob = scn.objects.active
        if ob.type == 'Mesh':
            me = ob.getData(mesh=True)
            #faces = [me.faces[i] for i in range(min(widget["lim_number"].val,len(me.faces))) if me.faces[i].sel==1]
            faces = []
            for face in me.faces:
                if len(faces) <  widget["lim_number"].val:
                    if face.sel:
                        faces.append(face)
                else:
                    break
            drawFacesBR(me, faces, ob.matrix)
            
    if widget["SZA_toggle"].val == 1:    
        scn = Blender.Scene.GetCurrent()
        ob = scn.objects.active
        if ob.type == 'Mesh':
            me = ob.getData(mesh=True)
            #faces = [me.faces[i] for i in range(min(widget["lim_number"].val,len(me.faces))) if me.faces[i].sel==1]
            faces = []
            for face in me.faces:
                if len(faces) <  widget["lim_number"].val:
                    if face.sel:
                        faces.append(face)
                else:
                    break
            drawFacesZA(me, faces, ob.matrix)
            
    if widget["SZZ_toggle"].val == 1:    
        scn = Blender.Scene.GetCurrent()
        ob = scn.objects.active
        if ob.type == 'Mesh':
            me = ob.getData(mesh=True)
            #faces = [me.faces[i] for i in range(min(widget["lim_number"].val,len(me.faces))) if me.faces[i].sel==1]
            faces = []
            for face in me.faces:
                if len(faces) <  widget["lim_number"].val:
                    if face.sel:
                        faces.append(face)
                else:
                    break
            drawFacesZZ(me, faces, ob.matrix)