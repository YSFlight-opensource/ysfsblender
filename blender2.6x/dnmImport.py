# -*- coding: utf-8 -*-

from logging import getLogger
from logging.config import fileConfig

from mathutils import Vector
import bpy

from ysfs_lib.common import Color

def float2(s):
    posE = s.find("e")
    if posE != -1:
        posDOT = s.find(".", posE)
        if posDOT != -1:
            s = s[:posDOT]
    return float(s)

def tuplesToVector(t1, t2):
    return Vector((t2[0]-t1[0], t2[1]-t1[1], t2[2]-t1[2]))


class Face:
    def __init__(self,  material="shadeless"): 
        self.normal   = None
        self.vertices = None # Vert order
        self.color    = None
        self.bright   = False
        self.number   = 0
        self.material = material
        
    def computeFace(self, verts):
        for att in self.__dict__:
            if att == None:
                raise Exception('Incomplete face')
        if len(verts)<3:
            raise Exception('Incomplete face : less than 3 vertices')
        
        v1 = tuplesToVector(verts[self.vertices[1]], verts[self.vertices[2]])
        v2 = tuplesToVector(verts[self.vertices[1]], verts[self.vertices[0]])
        if v1.cross(v2).dot(self.normal) < 0:
            self.vertices.reverse()
        
class FaceReader:
    def __init__(self, fd):
        self.fd = fd
        self.face = Face()
    
    def readColor(self, col):
        # Color of a face
        if len(col) == 2:  #24 bit color conversion
            rgbCol = Color()
            try:
                col = int(col[1])
                if (col>32767) or (col<0):
                    self.logger.warning("24 bits colors must be between 0 and 32767")
                    col = 32767
            except:
                self.logger.warning("Invalid Color")
                col = 32767
            rgbCol.from24b(col)   
        else:                  #RGB
            try:
                rgbCol = Color(int(col[1]), int(col[2]), int(col[3]))
            except:
                self.logger.warning("Invalid color")
                rgbCol = Color(255, 255, 255)
        self.color = rgbCol
        
        
    def readNormal(self, data):
        # Reading Normals and median points
        try:
            y, z, x = map(float2, data[4:])
        except:
            self.logger.warning("Invalid normal")
            x, y, z = 0, 0, 0
        normal = Vector((x, -y, z))
        self.face.normal = normal
        
    def readVertices(self, data):
        # The vertices of the face
        try:
            vertOrder = list(map(int, data[1:]))
            # Check a vertID doesn't appear twice, eg 2,4,5,2 -> 2,4,5 else we have problems
            self.face.vertices = vertOrder
        except:
            self.logger.error("Invalid vertOrder")
    
    
    def readFace(self, verts):
        while True:
            line = self.fd.readline()
            if line == "":
                break
            data = line.split()
            
            if data[0][0] == "C":
                self.readColor(data)
                    
            elif data[0] == "B":
                self.face.setBright()
                    
            elif data[0][0] == "N":
                self.readNormal(data)
    
            elif data[0][0] == "V":
                self.readVertices(data)
                
            elif data[0][0] == "E":    
                #ends face subsection
                self.face.computeFace(verts)
                break
                
        
class SRFReader:
    def __init__(self, fd, CNT = [0,0,0]):
        f=open("ysfs_lib/logging.ini")
        fileConfig(f)
        f.close()
        self.logger = getLogger("srfimport")
        self.fd = fd
        self.CNT = CNT
        
        self.mesh = bpy.data.meshes.new("Solid")
        self.vertices = []
        self.faces = []
        self.roundedVertices = []
        
        
    def readVertice(self, data):
        y, z, x = 0, 0, 0
        if data[-1] == "R":
            self.roundedVertices.append(True)
            try:
                y, z, x = map(float2, data[1:-1])  # rounded, will have to do a little face.smooth=1 
            except:
                self.logger.error("Cannot read the vertex coordinates")
        else:
            self.roundedVertices.append(False)
            try:
                y, z, x = map(float2, data[1:])      # not rounded
            except:
                self.logger.error("Cannot read the vertex coordinates")
        vertex = (x-self.CNT[2], -y+self.CNT[0], z-self.CNT[1]) # Blender X = z YS ; Blender Y = - x YS ; Blender Z = y YS
        self.vertices.append(vertex)
        
    
    def readFace(self):    
        faceReader = FaceReader(self.fd)
        faceReader.readFace(self.vertices)
        self.faces.append(faceReader.face.vertices)
        
        
    def readSRF(self):
        faceNB   = 0        
        while True:
            line = self.fd.readline()
            if line == "":
                break
            data = line.split()
            
            if len(data)>0: # it's not a blank line
                if data[0][0] == "V":
                    #importing a vertex
                    self.readVertice(data)
                    
                elif data[0][0] == "F":
                    # Start face section
                    faceNB += 1
                    self.readFace()
                    
                elif data[0][0] == "E":
                    # end
                    self.mesh.from_pydata(self.vertices, [], self.faces)
                    self.mesh.update()
                    break 
                
global_undo = bpy.context.user_preferences.edit.use_global_undo
bpy.context.user_preferences.edit.use_global_undo = False
scene = bpy.context.scene
                
fd = open("test.srf", "r")                
srfReader = SRFReader(fd)
srfReader.readSRF()

object = bpy.data.objects.new("Imported Object", srfReader.mesh)  
object.data = srfReader.mesh  
scene.objects.link(object) 

fd.close()
bpy.context.user_preferences.edit.use_global_undo = global_undo