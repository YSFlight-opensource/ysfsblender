# -*- coding: utf-8 -*-

## Common classes and functions to the export scripts

# Copyright 2012 Vincent A (Vincentweb)

from array import array
import bmesh
import mathutils
import bpy

from  ysfs_lib import config
from ysfs_lib.common import nl, Color


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

class Mesh:
    def __init__(self, blenderMesh):
        self.blendMesh       = blenderMesh
        self.vertsNotRounded = array('i')
        self.facesColor      = []
        self.facesMidPoint   = []
        
        # Select and go in edit mode before using the bmesh function
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        self.bm = bmesh.from_edit_mesh(blenderMesh)
        
        self.calcFaceMidpoint()
        self.calcRoundedVerts()
        bpy.ops.object.mode_set(mode='OBJECT')
        self.calcFacesColor()
        
        
        
    def calcRoundedVerts(self):
        # 1) Make the list of the not rounded vertices
        # 1.1) By analysing the face which are not smooth
        # Initialliy, all the vertices are rounded
        for _ in range(len(self.blendMesh.vertices)):
            self.vertsNotRounded.append(0)
        # All the vertices arround a smooth face are rounded
        for face in self.blendMesh.polygons:
            if face.use_smooth == 0:
                for vert_index in face.vertices:
                    self.vertsNotRounded[vert_index]=1
        # 1.2) By analysing the sharp edges ; 1 sharp edge -> vertices of the edges not round
        for edge in self.blendMesh.edges:
            if edge.use_edge_sharp:
                self.vertsNotRounded[edge.v1.index]=1
                self.vertsNotRounded[edge.v2.index]=1
                
    def calcFacesColor(self):
        # Requires OBJECT Mode
        if len(self.blendMesh.vertex_colors) > 0:
            vertcolor = 0
            for face in self.blendMesh.polygons:
                c = self.blendMesh.vertex_colors[0].data[vertcolor].color
                self.facesColor.append(Color(255*c.r, 255*c.g, 255*c.b))
                vertcolor += len(face.vertices) 
        else:
            for _ in self.blendMesh.polygons:
                self.facesColor.append(Color(255,255,255))
                
    def calcFaceMidpoint(self):
        # Suppose we have the faces in the same order
        for face in self.bm.faces:
            self.facesMidPoint.append(face.calc_center_median())
    
            
                
class MeshWriter:
    def __init__(self, mesh, fd):
        self.mesh   = mesh # Mesh object
        self.buffer = ""
        self.fd     = fd
        
    def write(self):
        # FIXME : write directly in fd rather than concatenate strings in buffer
        self.buffer += str('SURF'+nl())
        self.write_verts()
        self.write_faces()
        self.buffer+=str('E'+nl())
        self.fd.write(self.buffer)
        
    def write_verts(self):
        i = 0
        for vert in self.mesh.blendMesh.vertices:
            x, y, z = map(ff, (vert.co.x, -vert.co.y, vert.co.z))
            if self.mesh.vertsNotRounded[i] == 1:
                self.buffer+=str( 'V %s %s %s' % (y, z, x) ) # We go by the order Y, Z and X, because Blender Y = -YS X, Blender Z = YS Y, and Blender X = YS Z
            else: 
                self.buffer+=str( 'V %s %s %s R' % (y, z, x) ) 
            self.buffer+=str(nl())
            i += 1
            
    def write_faces(self):
        faceIndex = 0
        for face in self.mesh.blendMesh.polygons:
            self.buffer += 'F'+nl() # Declare that we are writing data about a face/polygon
            
            # -- Normal and midpoints
            ny, nz, nx = map(ff, (-face.normal.y, face.normal.z, face.normal.x))
            # face midpoint

            midpoint = self.mesh.facesMidPoint[faceIndex]
            my, mz, mx = map(ff, (-midpoint.y, midpoint.z, midpoint.x))
            self.buffer += 'N %s %s %s %s %s %s%s' % (my, mz, mx, ny, nz, nx, nl())
            
            
            # -- Colors
            col = self.mesh.facesColor[faceIndex]
            if config.use24bitColor == True:
                col.calc24b()
                self.buffer += 'C %d%s' % (col.col24, nl()) # Write the color of this face
            else:
                self.buffer += 'C %d %d %d%s' % (col.r, col.g, col.b, nl())
            # Write brightness
            if col.brightness == 1:
                self.buffer += 'B'+nl()
            
            # -- Face vertices
            self.buffer+=str('V ')
            buff = ""
            # FIXME : cut too long list
            for vert_index in face.vertices:
                buff += str(vert_index)+" "
            self.buffer+=str(buff.rstrip()+''+nl()) # Write the index of each vertex and remove the final space for dnmViewer compatibility
            self.buffer+=str('E'+nl()) # End of face
            faceIndex +=1
