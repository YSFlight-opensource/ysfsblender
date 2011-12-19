## Common classes and functions to the export scripts

# Copyright 2009 Josiah H (Cobra) and Vincent A (Vincentweb)
# Script started by Josiah H (Cobra) and revised by Vincent A (Vincentweb)
# Credits to the Wikibook Noobs to Pro

#TODO: convert 1.500000001 -> 1.5

import Blender
from libysfs import *
from ysfsConfig import *
from Blender import sys,  Window,  Scene, NMesh, Mathutils
import bpy

#Convert decimal int to binary string
binary = lambda i, c = (lambda i, c: i and (c(i >> 1, c) + str(i & 1)) or ''): c(i, c) 

# Format Float to remove the useless 0
def ff(x):
    n = str(round(x, 4))
    n = n.rstrip('0')
    n = n.rstrip('.')
    if n=="-0":
        n='0'
    return n
    

def normal3pts(vert0,  vert1,  vert2): 
    vec1 = Vector()
    vec2 = Vector()
    v0 = Vertex(vert0.co.x, vert0.co.y, vert0.co.z)
    v1 = Vertex(vert1.co.x, vert1.co.y, vert1.co.z)
    v2 = Vertex(vert2.co.x, vert2.co.y, vert2.co.z)
    vec1.vert2vert(v0, v1)
    vec2.vert2vert(v0, v2)
    return crossProd(vec1, vec2)


def writeSRF(ob, isSRF=False):
    buffer = ""
    faceIndex = 0
    is_za = []
    is_zz = []
    is_zl = []
    za = []
    zz = []
#    transparency = []
#    transparencyLevel = []
    mesh = ob.getData(mesh=1) ## to modify
    mats=ob.getData(mesh=1).materials
    matUseVertCol = [False for i in range(len(mats)) ]
    for i in range(len(mats)):
        mat = mats[i]
        b = str(binary(mat.getMode()))
        b = b[::-1] # reverse b
        matUseVertCol[i] = bool(int(b[7]))
#        print mat.name
#        print b[7]
#        print matUseVertCol[i]
    

    # 1) Make the list of the not rounded vertices
    vertsNotRounded = [] 
    # 1.1) By analysing the face which are not smooth
    for i in range(len(mesh.verts)):
        vertsNotRounded.append(0)
    for face in mesh.faces:
        if face.smooth == 0:
            for vert in face.v:
                vertsNotRounded[vert.index]=1
    # 1.2) By analysing the sharp edges ; 1 sharp edge -> vertices of the edges not round
    for edge in mesh.edges:
        b = str(binary(edge.flag))
        b = b[::-1] # reverse b        
        if len(b)>9 and b[9]=='1':
            vertsNotRounded[edge.v1.index]=1
            vertsNotRounded[edge.v2.index]=1
            
    
    # Begin with the tag "SURF" to show that this is a valid SURF file
    buffer+=str('SURF'+nl()) 
    i = 0
    for vert in mesh.verts:
        if isSRF:
            x, y, z = vert.co.x, vert.co.y,  vert.co.z
#            x, y, z = vert.co.x-ob.LocX, vert.co.y-ob.LocY,  vert.co.z-ob.LocZ
#            [sx,sy,sz] = ob.getSize()
#            x, y, z = x*sx, y*sy, z*sz
            v = Mathutils.Vector(x, y, z)
            v = ob.mat.rotationPart().transpose()*v+ob.mat.translationPart()
#            v = (Mathutils.Matrix().rotationPart().zero()-ob.mat.rotationPart())*v+ob.mat.translationPart()
#            v.rotX(ob.RotX)
#            v.rotY(ob.RotY)
#            v.rotZ(ob.RotZ)
            x, y, z = v.x, v.y, v.z
        else:
            x, y, z = vert.co.x, vert.co.y,  vert.co.z
            [sx,sy,sz] = ob.getSize()
            x, y, z = x*sx, y*sy, z*sz
        x, y, z = map(ff, (x, -y, z))
        if vertsNotRounded[i] == 1: 
            
            buffer+=str( 'V %s %s %s' % (y, z, x) ) # We go by the order Y, Z and X, because Blender Y = -YS X, Blender Z = YS Y, and Blender X = YS Z
        else: 
            buffer+=str( 'V %s %s %s R' % (y, z, x) ) 
        buffer+=str(nl())
        i += 1  
    
    # Write the faces data
    for face in mesh.faces:
        buffer+=str('F'+nl()) # Declare that we are writing data about a face/polygon
        
        # Calculate the color data
        col = Color(255,255,255)
#        print face.mat
#        print mats
#        print matUseVertCol[face.mat]
        skipMats = False
        if len(mats) == 0:
            skipMats = True
        else:
            try:
                mat = mats[face.mat]
            except:
                print "WARNING: the script failed to find the proper material for "+ob.name
                print "------- START INFO -----------"
                print face.index
                print mats
                print face.mat
                print "------- END INFO -----------"
                skipMats = True
            
        if (skipMats == True) or (matUseVertCol[face.mat] == True):
            if(mesh.vertexColors):
                cl = face.col[0]
                bright = 0
                if mesh.faceUV:
#                    print face.mode
                    b = str(binary(face.mode))
                    b = b[::-1] # reverse b
#                    print b[4]
                    if len(b)>4 and b[4]=='1':
#                        print "bright"
                        bright = 1
                col = Color(cl.r, cl.g, cl.b, 0, bright)
            
        else:
            emit = 0
            if mat.emit >=1:
                emit = 1
            col = Color(int(mat.R*255), int(mat.G*255), int(mat.B*255),  0, emit)
#            print col.toStr()
        # Caculate transparency
#        transp = False
        transpLevel = 128
        isthere_za = False
        isthere_zz = False
        if (skipMats == False) and (mat.alpha != 1):
#            transp  = True
            transpLevel = int((mat.alpha*-1+1)*256)
            isthere_za = True
        if mesh.faceUV:
            b = str(binary(face.mode))
            b = b[::-1] # reverse b
            if len(b)>8 and b[8]=='1':
                is_zl.append(faceIndex)         
            if len(b)>12 and b[12]=='1':
                is_zz.append(faceIndex)
            if face.transp==2:
#                transp = True
                if face.image == None:					
                    isthere_za = True
                elif face.image.name[0:2]=="za":
                    isthere_za = True
                    transpLevel = int(face.image.name[2:-4].replace(".png", ""))
##                elif face.image.name[0:2]=="zz":
##                    isthere_zz = True
##                    transpLevel = int(face.image.name[2:-4].replace(".png", ""))
                else:
                    isthere_za = True
#        if transp:
        if isthere_za:
            is_za.append(faceIndex)
            za.append(transpLevel)
##            zz.append(transpLevel)
#            transparency.append(faceIndex)
#            transparencyLevel.append(transpLevel)
#            print "transp: "+str(transpLevel)
        # Write the color
        if use24bitColor == True:
            col.calc24b()
            buffer+=str('C %d' % (col.col24)) # Write the color of this face
            buffer+=str(nl())
        else:
            buffer+=str('C %d %d %d' % (col.r, col.g, col.b))
            buffer+=str(nl())
        # Write brightness
        if col.brightness == 1:
            buffer+=str('B')
            buffer+=str(nl())
            
            
##        if len(face.v) == 4: 
##            normalVec = normal3pts(face.v[0], face.v[1], face.v[2]) 
##            vect = normal3pts(face.v[0], face.v[2], face.v[3]) 
##            normalVec+=vect
##        else: 
##            normalVec = normal3pts(face.v[0], face.v[1], face.v[2]) 
        normalVec = Vector(face.no.x, face.no.y, face.no.z)
        normalVec.normalize()
        # Calculate the normal
        if mesh.faceUV:
#            if face.transp==2:
#                transparency.append(faceIndex)
            b = str(binary(face.mode))
            b = b[::-1] # reverse b
            if len(b)>9 and b[9]=='1':
               normalVec = Vector()
            
            #FIXME: #TODO:BAD!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #if len(b)>=10 and b[-10]=='1':
                # The face is double sided
             #   normalVec = Vector()
#        normalVec.cout() 
        # Write the gravity center and the normal of this face;
        midpt = Mathutils.Vector(face.cent.x, face.cent.y, face.cent.z)
        normalVec = Mathutils.Vector(normalVec.x, normalVec.y, normalVec.z)
        if isSRF:
            midpt = ob.mat.rotationPart().transpose()*midpt+ob.mat.translationPart()
            normalVec = ob.mat.rotationPart().transpose()*normalVec
#            midpt.rotX(ob.RotX)
#            midpt.rotY(ob.RotY)
#            midpt.rotZ(ob.RotZ)
#            normalVec.rotX(ob.RotX)
#            normalVec.rotY(ob.RotY)
#            normalVec.rotZ(ob.RotZ)
        fy, fz, fx, ny, nz, nx = map(ff, (-midpt.y, midpt.z, midpt.x, -normalVec.y, normalVec.z, normalVec.x))
        buffer+=str('N %s %s %s %s %s %s' % (fy, fz, fx, ny, nz, nx)) 
        buffer+=str(nl())
#        buffer+=str('N %f %f %f %f %f %f'+nl() % (-face.cent.y, face.cent.z, face.cent.x, -face.no.y, face.no.z, face.no.x)) 
        
        buffer+=str('V ') # Declare that were are writing which vertices that this face is connect to
        buff = ""
        for vert in face.v:
            buff += str(vert.index)+" "
        buffer+=str(buff.rstrip()+''+nl()) # Write the index of each vertex and remove the final space for dnmViewer compatibility
        buffer+=str('E'+nl()) # We are done writing about this face, put an E for END
        faceIndex +=1
        
    buffer+=str('E'+nl()) # On the last object, put an extra E there to declare that we are done with the whole file

#    print "transparency"
#    print transparency
    if not(isSRF):
        if is_za != []:
            for i in range(len(is_za)):
                if i%10 == 0:
                    buffer+=str(nl())
                    buffer+=str('ZA')
                buffer+=str(' %d %d' % (is_za[i], za[i]))
        buffer+=str(nl())
        if is_zz != []:
            for i in range(len(is_zz)):
                if i%10 == 0:
                    buffer+=str(nl())
                    buffer+=str('ZZ')
                buffer+=str(' %d' % (is_zz[i]))
        buffer+=str(nl())
        if is_zl != []:
            for i in range(len(is_zl)):
                if i%10 == 0:
                    buffer+=str(nl())
                    buffer+=str('ZL')
                buffer+=str(' %d' % (is_zl[i]))
        buffer+=str(nl())+str(nl())
 
    
    return buffer
