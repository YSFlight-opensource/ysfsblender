#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'Auto calculate the position of the camera'
Blender: 236
Group: 'Misc'
Tooltip: 'Calculate the best camera position which uses all the screens for a given orientation'
"""


import Blender
import math
from Blender import Window, Scene
from Blender.Mathutils import *

def highest(v1, v2):
    return v1.y<v2.y and v2 or v1

def lowest(v1, v2):
    return v1.y<v2.y and v1 or v2

def rightmost(v1, v2):
    return v1.x<v2.x and v2 or v1

def leftmost(v1, v2):
    return v1.x<v2.x and v1 or v2

def middle(v1, v2):
    return 0.5*(v1+v2)

class BoundingBox:
    def __init__(self, bb=[Vector(), Vector(), Vector(), Vector(), Vector(), Vector(), Vector(), Vector()]):
        self.coords   = bb
        self.update()
        
    def update(self):
        self.length_x()
        self.length_y()
        self.length_z()
        self.diago()
        self.is_y_length_longer()   
        self.calc_center()
        self.calc_face_median_pts()
        
    def union(self, bb):
        self.coords[0] = Vector(min(self.coords[0].x, bb.coords[0].x), min(self.coords[0].y, bb.coords[0].y), min(self.coords[0].z, bb.coords[0].z))
        self.coords[1] = Vector(min(self.coords[1].x, bb.coords[1].x), min(self.coords[1].y, bb.coords[1].y), max(self.coords[1].z, bb.coords[1].z)) 
        self.coords[2] = Vector(min(self.coords[2].x, bb.coords[2].x), max(self.coords[2].y, bb.coords[2].y), max(self.coords[2].z, bb.coords[2].z))
        self.coords[3] = Vector(min(self.coords[3].x, bb.coords[3].x), max(self.coords[3].y, bb.coords[3].y), min(self.coords[3].z, bb.coords[3].z))
        self.coords[4] = Vector(max(self.coords[4].x, bb.coords[4].x), min(self.coords[4].y, bb.coords[4].y), min(self.coords[4].z, bb.coords[4].z))
        self.coords[5] = Vector(max(self.coords[5].x, bb.coords[5].x), min(self.coords[5].y, bb.coords[5].y), max(self.coords[5].z, bb.coords[5].z))
        self.coords[6] = Vector(max(self.coords[6].x, bb.coords[6].x), max(self.coords[6].y, bb.coords[6].y), max(self.coords[6].z, bb.coords[6].z))
        self.coords[7] = Vector(max(self.coords[7].x, bb.coords[7].x), max(self.coords[7].y, bb.coords[7].y), min(self.coords[7].z, bb.coords[7].z))
        self.update()
        
    def length_x(self):
        self.x_length = (self.coords[4] - self.coords[0]).length
        
    def length_y(self):
        self.y_length = (self.coords[3] - self.coords[0]).length
        
    def length_z(self):
        self.z_length = (self.coords[1] - self.coords[0]).length
                
    def diago(self):
        self.diagonal = (self.x_length**2+self.y_length**2+self.z_length**2)**(0.5)
        
    def calc_center(self):
        self.center = self.coords[0] + 0.5*(self.coords[3]-self.coords[0]) + 0.5*(self.coords[4]-self.coords[0]) + 0.5*(self.coords[1]-self.coords[0])

    def calc_face_median_pts(self):
        self.face_median_pts = []
        self.face_median_pts.append(middle(self.coords[0], self.coords[2]))
        self.face_median_pts.append(middle(self.coords[0], self.coords[5]))
        self.face_median_pts.append(middle(self.coords[5], self.coords[7]))
        self.face_median_pts.append(middle(self.coords[7], self.coords[2]))
        self.face_median_pts.append(middle(self.coords[5], self.coords[2]))
        self.face_median_pts.append(middle(self.coords[0], self.coords[7]))
        
    def is_y_length_longer(self):
        self.y_longer = self.y_length >= self.x_length and self.y_length >= self.z_length
        
        
    def __str__(self):
        return "[bbox: left:%.2f, %.2f, %.2f, %.2f, right:%.2f, %.2f, %.2f, %.2f]" % (self.coords[0], self.coords[1], self.coords[2], self.coords[3], self.coords[4], self.coords[5], self.coords[6], self.coords[7])


class Calculate_Camera_Position:
    def __init__(self, scenary=Scene.GetCurrent()):
        self.sce     = scenary
        self.xcoef = 1
        self.ycoef = 1                
        
    def calculate_best_position(self, focusOn="all", areaPercentOnCameraToUse=100, camera_width=1, camera_height=1):
        if camera_width < camera_height:
            self.xcoef = float(camera_width)/camera_height
        elif camera_width > camera_height:
            self.ycoef = float(camera_height)/camera_width
        self.camera  = self.find_camera()
        self.f       = self.camera.getData().lens/16. # Real focal length
        if focusOn == "cut_wings":
            self.boundingBox = self.unionAllBoundingBoxYlonger()
        else:
            self.boundingBox = self.unionAllBoundingBox()
            
##        print 201, self.boundingBox.x_length, self.boundingBox.y_length, self.boundingBox.z_length, self.boundingBox.diagonal
            
        self.margin    = areaPercentOnCameraToUse/100.
        self.epsilon   = self.camera_basis()
        self.put_camera_on_good_side() #put the camera on the good side of the object
        self.new_camera_position(focusOn)
        self.new_camera_position(focusOn)
#        self.new_camera_position(focusOn) #We sometimes need 2 calculations since the extremal vertice change when you move the camera

        
        
    def find_camera(self):
        for ob in self.sce.objects:
            if ob.getType() == "Camera":
                return ob
                break
        #No camera found, we create one
        print "no camera was found"
        camdata = Camera.New('persp')           # create new camera data
        camdata.name = 'newCam'
        camdata.lens = 35.0
        camera = self.sce.objects.new(camdata,'Camera')
        return camera
            
    def camera_basis(self):
        #mat = self.euler.toMatrix()
        mat = self.camera.mat.rotationPart()
        e1 = Vector(1,0,0)
        e2 = Vector(0,1,0)
        e3 = Vector(0,0,1)
##        print self.euler
        mat.transpose()
        #print mat
        ep1 = mat*e1
        ep2 = mat*e2
        ep3 = mat*e3
        #print [ep1, ep2, ep3]
        return [ep1, ep2, ep3]
    
    def put_camera_on_good_side(self):
        pos = self.epsilon[2]*self.boundingBox.diagonal+self.boundingBox.center
##        print self.boundingBox.x_length, self.boundingBox.y_length, self.boundingBox.z_length
##        print self.boundingBox.diagonal
##        print self.boundingBox.center
##        print pos
        pos.resize4D()
        camera_matrix  = self.camera.mat
        camera_matrix[3] = pos
        self.camera.setMatrix(camera_matrix)
    
    def projectedOnCamera(self, vector):
##        print "proj1"
##        print vector
        projected = self.camera.mat.rotationPart()*vector - self.camera.mat.rotationPart()*self.camera.mat.translationPart()
        projected.z = -projected.z
        if projected.z != 0:
            projected.x*= self.f/projected.z
            projected.y*= self.f/projected.z
        else:
            projected.x*=0.1
            projected.y*=0.1
##        print projected
        return projected
    
    def projection2(self, vector):
##        print "proj"
##        print vector
        projected = self.camera.mat.rotationPart()*vector - self.camera.mat.rotationPart()*self.camera.mat.translationPart()
        projected.z = -projected.z
##        print projected
        return projected
    
    def findExtremalVertices(self, vertices):
        vert_nb = 0
        for v in vertices:
            vert_nb += 1
            vp = self.projectedOnCamera(v)
            v  = self.projection2(v)
            if vert_nb == 1:
                vhighest2   = vp.copy()
                vlowest2    = vp.copy()
                vrightmost2 = vp.copy()
                vleftmost2  = vp.copy()
                vhighest3   = v.copy()
                vlowest3    = v.copy()
                vrightmost3 = v.copy()
                vleftmost3  = v.copy()
            else:
                if vp.y > vhighest2.y:
                    vhighest2 = vp
                    vhighest3 = v
                if vp.x > vrightmost2.x:
                    vrightmost2 = vp
                    vrightmost3 = v
                if vp.y < vlowest2.y:
                    vlowest2 = vp
                    vlowest3 = v
                if vp.x < vleftmost2.x:
                    vleftmost2 = vp
                    vleftmost3 = v
              
##        print [vrightmost3, vhighest3, vleftmost3, vlowest3]
##        print [vrightmost2, vhighest2, vleftmost2, vlowest2]
        return [vrightmost3, vhighest3, vleftmost3, vlowest3]
    
    def calculate_translations(self, focusOn):
        #print self.xcoef, self.ycoef
        if focusOn == "face_median_pts":
            ve = self.findExtremalVertices(self.boundingBox.face_median_pts)
        else:
            ve = self.findExtremalVertices(self.boundingBox.coords)
        self.ve = ve
        # After solving our Cramer systems
        p1 = ve[0].x - self.xcoef*self.margin*ve[0].z/self.f
        p2 = ve[2].x + self.xcoef*self.margin*ve[2].z/self.f
        p3 = ve[1].y - self.ycoef*self.margin*ve[1].z/self.f
        p4 = ve[3].y + self.ycoef*self.margin*ve[3].z/self.f
        z1 = self.f*(p1-p2)/(2.*self.xcoef*self.margin)
        z2 = self.f*(p3-p4)/(2.*self.ycoef*self.margin)
##        print [p1, p2, p3, p4]
##        print [z1, z2]
        if z2 > z1:
##            print "opt1 y fixed"
            z = z2
            
            y = (p3+p4)/2.
            p1 = ve[0].x - self.xcoef*self.margin*(ve[0].z + z)/self.f
            p2 = ve[2].x + self.xcoef*self.margin*(ve[2].z + z)/self.f
            if p1<0 and 0<p2:
                x = 0
            else:
                x = (p1+p2)/2
            
        else:
##            print "opt2 x fixed"
            z = z1
            
            x = (p1+p2)/2.
            p3 = ve[1].y - self.ycoef*self.margin*(ve[1].z + z)/self.f
            p4 = ve[3].y + self.ycoef*self.margin*(ve[3].z + z)/self.f
            if p3<0 and 0<p4:
                y=0
            else:
                y = (p3+p4)/2
            #y = (ve[1].y - self.margin*(ve[1].z + z)/self.f + ve[3].y + self.margin*(ve[3].z + z)/self.f)/2.
            
##        print [x, y, z]
        return [x, y, z]
        
    def new_camera_position(self, focusOn):
        translate_in_eps = Vector(self.calculate_translations(focusOn)) # in the epsilon basis
        translate_canon  = self.camera.mat.rotationPart().transpose() * translate_in_eps # in canonical bases (e1, e2, e3)
        #camera_location  = self.calculate_camera_position() + translate_canon
        camera_location  = self.camera.mat.translationPart() + translate_canon
        camera_location.resize4D()
        camera_matrix    = self.camera.mat
        camera_matrix[3] = camera_location
        self.camera.setMatrix(camera_matrix)
##        print "dist: "+str(((self.camera.LocX)**2+(self.camera.LocY)**2+(self.camera.LocZ)**2)**(0.5))
##        print "diag: "+str(self.boundingBox.diagonal)
        self.camera.getData().setClipEnd(((self.camera.LocX)**2+(self.camera.LocY)**2+(self.camera.LocZ)**2)**(0.5)+self.boundingBox.diagonal)
        
    def force_y_center(self):      
        camera_location  = self.camera.mat.translationPart() + self.camera.mat.rotationPart().transpose() *Vector(0,self.projection2(self.boundingBox.center).y,0)
        camera_location.resize4D()
        camera_matrix    = self.camera.mat
        camera_matrix[3] = camera_location
        self.camera.setMatrix(camera_matrix)
        #print self.boundingBox.center
                
            
    def unionAllBoundingBox(self):
        unionAllBB = BoundingBox()
        nb_object = 0
        for ob in self.sce.objects:
            #print ob.name
            if ob.type == 'Mesh':
                nb_object += 1
                bb = BoundingBox(ob.boundingBox)
                if nb_object == 1:
                    unionAllBB = BoundingBox(bb.coords[:])
                else:
                    unionAllBB.union(bb)
        return unionAllBB

    def unionAllBoundingBoxYlonger(self):
        unionAllBB = BoundingBox()
        nb_object = 0
        for ob in self.sce.objects:
            if ob.type == 'Mesh':
                nb_object += 1
                bb = BoundingBox(ob.boundingBox)
                if bb.y_longer:
                    if nb_object == 1:
                        unionAllBB = BoundingBox(bb.coords[:])
                    else:
                        unionAllBB.union(bb)
        return unionAllBB
    
if __name__ =='__main__':    
    print "--------NEW Caculation----------"

    calc = Calculate_Camera_Position()
    
    camera = calc.find_camera()
##    camera.setEuler   (Euler(1.22173, 0, 0.610865))
    #camera.setLocation(Vector(40, -40, 12))
    #calc.calculate_best_position("face_median_pts", 100)
    calc.calculate_best_position("all", 100, Scene.GetCurrent().render.sizeX, Scene.GetCurrent().render.sizeY)
    
