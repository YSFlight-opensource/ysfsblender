#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'surf (.srf) and DynaModel (.dnm)...'
Blender: 236
Group: 'Import'
Tooltip: 'Import YSFlight 3D format (.srf)'
"""

#Blender: 236 because of the Center New function

#FIXME: CHANGE AXIS SIDE VIEW -> FRONT VIEW

__author__ = "VincentWeb"
__url__ = ("blender", "",
"Author's homepage, http://shadowhunters.yspilots.com")
__version__ = "1.309" #approximately: number of lines/1000

__bpydoc__ = """\
This script imports Surf files to Blender

Installation:
Linux -> go to /home/username
Windows -> go to C:\Program Files\Blender Foundation\Blender
- copy/paste the script in your ./blender/script
- Open Blender
- Go in the script window
- in the menu Scripts, select Update Menu

Usage:
Run this script from "File->Import" menu and then load the desired SURF file.
"""


#FIXME: replace "from x import all" to import x and reload(x)
#FIXME: detect the modifier non applied
#FIXME: supprimer les doublons après la triangulation, pas avant sinon on empêche la création de trous.
#TODO: import polygons with assignVertsToGroup(
#TODO: fix the problem of faces with holes
#TODO: put the not run scripts in a separated directory
#TODO: select one object at the end
#TODO: clean-up unused functions
#TODO: for a face with more than 4 vertices (which is cut into x faces), if one of it's vertices is rounded, should we smooth the x cut faces (the whole original face) or only smooth the cut faces containing this vertex?
#TODO: write information about the faces cut by the script into a file

#BRI = B

# Copyright 2009 Vincent A (Vincentweb)
print "---------------------------------------"
try: 
    import psyco; psyco.full() 
except: 
    pass

# For Linux users, we append the /.blender/scripts/blender folder in the sys.path
import sys, math,  time,  os

TEST_MODE = False
for path in sys.path:
#    if path.find("home/vincentweb"):
#        TEST_MODE = True
    if path[-17:] == '/.blender/scripts':
        sys.path.append(path+'/blender')

from ysfsConfig import *
from libysfs import *
from string import *
from datetime import datetime

for path in sys.path:
    if path == u'/home/vincentweb/.blender/scripts':
        TEST_MODE = False
        break
        
        
if TEST_MODE == False:
    import Blender, meshtools,  bpy #either here, either below, but not both
    from Blender import *
    from Blender.Window import *
else:
    print "DEBUGGING MODE"

debug = False
if os.path.exists('/home/vincentweb/tmp'):
    print "Debug Mode"
    debug = True

e = Error()
w = Warning()
log = Log("logYSFSimport.txt", debug)

##hasimage = []
##image    = []
##for i in range(257):
##    try:
##        image.append(Image.Load(Blender.Get('scriptsdir')+"/blender/lib_ysfs/tex/tex"+str(i)+".png"))
##        hasimage.append(True)
##    except:
##        try:
##            image.append(Image.Load(Blender.Get('scriptsdir')+"/lib_ysfs/tex/tex"+str(i)+".png"))
##            hasimage.append(True)
##        except:
##            hasimage.append(False) # had nothing to do here
##            image.append(None)
##            print "Failed to find the picture tex"+str(i)+".png"
zatex = Ztex("za")
#zztex = Ztex("zz")

if not(zatex.success):
    e.outl(0, "Failed to load some ZA textures, see the console.")
#if not(zztex.success):
 #   e.outl(0, "Failed to load some ZZ textures, see the console.")

# To convert 2e-005.0 to 2e-005, else Python don't like
def float2(s):
	posE = s.find("e")
	if posE != -1:
		posDOT = s.find(".", posE)
		if posDOT != -1:
			s = s[:posDOT]
	return float(s)

## ----------- Geometry functions and classes --------------------

class VertPoly(Vertex):
        #Those vertices contains also a coefficient which is the distance from the center of the polygon
        def __init__(self, x=0, y=0, z=0,  round=0):
            Vertex.__init__(self, x, y, z,  round)
            self.distCenter = 0
            self.next = ""
            self.prev = ""

class Polygon:
            
    def __init__(self, vertList, vertOrder, normal):
        self.vertList = vertList
        self.vertOrder = vertOrder
        self.normal = normal
        self.blenderPoly = []
        self.update2()
        try:
            if self.vertOrder[0] != self.vertOrder[len(self.vertOrder)-1]:
                self.vertOrder.append(self.vertOrder[0])
        except:
            e.outl(0,  "Problem with vert order maybe null, length: "+str(len(self.vertOrder))+" list: " +str(self.vertOrder))
        
    def update(self):
        # make an other triangulation in case some vertices changed
        self.center = self.calcCenter() # Gravity center of the poly
        self.dist2Center()
        self.orientation = self.polyOrientation() # Orientation of the vertices: 1= Counter clockwise
        self.facesTrig = []
        self.faces = []
        self.clipEars()
        if triangulate == False:
            self.joinTrig()
        else:
            self.faces = self.facesTrig
        
    def update2(self):
        self.createBlenderPoly()
        facesTrig = Blender.Geometry.PolyFill([self.blenderPoly])
        self.facesTrig= []
        for f in facesTrig:
            if len(set([self.vertOrder[f[0]], self.vertOrder[f[1]], self.vertOrder[f[2]]])) == 3:
                fList = [self.vertOrder[f[0]], self.vertOrder[f[1]], self.vertOrder[f[2]]]
                self.facesTrig.append(fList)
        if TEST_MODE:
            print "****"
            for face in self.facesTrig:
                print face
        if triangulate == False:
            self.joinTrig()
        else:
            self.faces = self.facesTrig
        
    def createBlenderPoly(self):
        for vo in self.vertOrder:
            self.blenderPoly.append(Blender.Mathutils.Vector(self.vertList[vo].x, self.vertList[vo].y, self.vertList[vo].z))
        
    def calcCenter(self,  newVertOrder = 0):
        if newVertOrder ==0:
            newVertOrder = self.vertOrder
        #calculates the gravity center of the poly
        center = Vertex()
        prev = VertPoly()
        for vo in newVertOrder:
            center+=self.vertList[vo]
            self.vertList[vo] = VertPoly(self.vertList[vo].x, self.vertList[vo].y, self.vertList[vo].z,  self.vertList[vo].round)            
            self.vertList[vo].prev = prev
            prev.next = self.vertList[vo]
            prev = self.vertList[vo]
        self.vertList[newVertOrder[0]].prev = self.vertList[vo]
        self.vertList[vo].next = self.vertList[newVertOrder[0]]
        center.scal(len(self.vertOrder))
        return center
        
    def dist2Center(self):    
        #Update the attribute distCenter of the vertices (distance betwwen the vertex and the center)
        for vo in self.vertOrder:
            self.vertList[vo].distCenter = self.vertList[vo].distance2(self.center)
            
    def polyOrientation(self):
        #Calculate the orientation of the vertices of the poly
        maxDist = 0
        maxDistVert = VertPoly()
        for vo in self.vertOrder:
            if self.vertList[vo].distCenter > maxDist:
                maxDist = self.vertList[vo].distCenter
                maxDistVert = self.vertList[vo]
        # maxDistVert is a convex vertex because it is the furthest of the center, so we can use it to get the orientation of the poly
        v1v0 = Vector()
        v1v2 = Vector()
        v1v0.vert2vert(maxDistVert, maxDistVert.prev)
        v1v2.vert2vert(maxDistVert, maxDistVert.next)
        if TEST_MODE == True:
            print "orientation: "
            print orientation3D(v1v2, v1v0, self.normal)
        return orientation3D(v1v2, v1v0, self.normal) #1=Counter Clockwise, -1 = Clockwize
        
    def isConvex(self, iV1, iV2, iV3):
        v2v1 = Vector()
        v2v3 = Vector()
        v2v1.vert2vert(self.vertList[iV2], self.vertList[iV1])
        v2v3.vert2vert(self.vertList[iV2], self.vertList[iV3])
        debug = orientation3D(v2v1, v2v3, self.normal)
#        v2v1.cout()
#        v2v3.cout()
#        self.normal.cout()
#        if orientation3D(v2v1, v2v3, self.normal) == 1:
        if orientation3D(v2v3, v2v1, self.normal) == 1:
            return True
        else:
            return False
            
    def concaveVertFace(self, face):
        k = 0
        for i in range(len(face)):
            debug = not(self.isConvex(face[(i-1)%len(face)], face[i], face[(i+1)%len(face)]))
            if not(self.isConvex(face[(i-1)%len(face)], face[i], face[(i+1)%len(face)])):
                if TEST_MODE == True:
                    print "found "+str(face[i])
                return k
            k+=1
        return 0
        
    def isAnEar(self, iV2):
        #Tells if v1,v2,v3 is an ear
        i = self.vertOrder.index(iV2)
        iV0, iV1, iV3, iV4 =  self.vertOrder[(i-2)%len(self.vertOrder)], self.vertOrder[(i-1)%len(self.vertOrder)], self.vertOrder[(i+1)%len(self.vertOrder)], self.vertOrder[(i+2)%len(self.vertOrder)]
        v2 = self.vertList[iV2]
        v1 = self.vertList[iV1]
        v0 = self.vertList[iV0]
        v3 = self.vertList[iV3]
        v4 = self.vertList[iV4]
        v1v2 = Vector()
        v3v2 = Vector()
        v1v3 = Vector()
        v1v0 = Vector()
        v3v4 = Vector()
        v1v2.vert2vert(v1, v2)
        v3v2.vert2vert(v3, v2)
        v1v3.vert2vert(v1, v3)
        v1v0.vert2vert(v1, v0)
        v3v4.vert2vert(v3, v4)
        debug_inSector = inSector3D(v1v2, v1v0, v1v3, self.normal, self.orientation) and inSector3D(v3v4, v3v2, -v1v3, self.normal, self.orientation)
        if debug_inSector:
            n = len(self.vertOrder)
            for i in range(len(self.vertOrder)):
                if (self.vertOrder[i] != iV1) and (self.vertOrder[i] != iV3) and (self.vertOrder[(i+1)%n]) != iV1 and (self.vertOrder[(i+1)%n]) != iV3: #don't test the side if it shares a vertex with it
                    debug = intersectLine3D(self.vertList[self.vertOrder[i]], self.vertList[self.vertOrder[(i+1)%n]], self.vertList[iV1], self.vertList[iV3], self.normal)
                    if debug:
                        return False
            return True
        else:
            return False
         
    def listFaceTrig(self, n):
        # Builds a list of trigonal faces
        l=[]
        i = 2
        prev = 1
        while i <n:
            l.append([0,prev,i])
            prev = i
            i+=1
        return l
         
    def clipEars(self):
        # We clip the ears to triangulise the poly, equivalent of Geometry::PolyFill()
#        vertOrder = list(self.vertOrder)
        k = 0
        stop = len(self.vertOrder)
        while len(self.vertOrder) > 3:
            k +=1
            if k>stop:
                e.outl(0, "ERROR: Tesselate failed ")
                print self.vertOrder
                # We have to build a fake faces list
                self.facesTrig= self.listFaceTrig(len(self.vertOrder))
                break
            for i in range(len(self.vertOrder)):
                if TEST_MODE == True:
                    print self.vertOrder[(i-1)%len(self.vertOrder)], self.vertOrder[i], self.vertOrder[(i+1)%len(self.vertOrder)]
                if self.isAnEar(self.vertOrder[i]):
                    if TEST_MODE == True:
                        print "one found "+str(self.vertOrder[i])
                    n = len(self.vertOrder)
                    self.facesTrig.append([self.vertOrder[(i-1)%n], self.vertOrder[i], self.vertOrder[(i+1)%n]])
                    self.vertOrder.remove(self.vertOrder[i])
                    break# to exit the loop so that we check again the first vertex of the loop, maybe it became now a convex one
                else:
                    if TEST_MODE == True:
                        print "failed"
                if len(self.vertOrder) == 3:
                    break
        if len(self.vertOrder) <4:
            self.facesTrig.append(self.vertOrder) # We add the one which remains
        if TEST_MODE == True:
            for face in self.facesTrig:
                print face

    def joinTrig(self):   
        # We join the triangulated faces to build 4 vertices poly
        quadFaceList = []
        debug = len(self.facesTrig)
        faceTrig = self.facesTrig#debug
        self.facesTrig.reverse() # so that we start with the first ear which is in a corner instead of the last ear
        while len(self.facesTrig) > 0:
            trigFace = self.facesTrig.pop()
    #        print "--"
    #        print trigFace
            trigFaceSet = set(trigFace)
            i = 0
            joined = False
            while (len(self.facesTrig) > 0) and (i<len(self.facesTrig)):
                trigFace2 = self.facesTrig.pop()
    #            print trigFace2
                trigFace2Set = set(trigFace2)
                unionSet = trigFace2Set|trigFaceSet
                if len(unionSet) == 4:
                    quadList = []
#                    For the old Triangulation algo
#                    quadList.append(trigFace[0])
#                    quadList.append(trigFace[1])
#                    quadList.append(trigFace[2])
#                    quadList.append((trigFace2Set-trigFaceSet).pop())
                    interSet = trigFace2Set&trigFaceSet
                    quadList.append((trigFace2Set-trigFaceSet).pop())
                    try:
                        quadList.append(interSet.pop())
                    except:
                        e.outl(0, "Failed to join trigs:")
#                        print trigFaceSet
#                        print trigFace2Set
#                        print "failed to join"
#                        print faceTrig
#                        print unionSet
#                        print interSet
                    quadList.append((trigFaceSet-trigFace2Set).pop())
                    try:
                        quadList.append(interSet.pop())
                    except:
                        e.outl(0, "Error of intersect " + str(trigFace2Set)+" " + str(trigFaceSet))
                    quadFaceList.append(translateList(quadList, 1))
#                    quadFaceList.append(translateList(quadList, self.concaveVertFace(quadList)))
                    joined = True
                    break
                else:
                    self.facesTrig.insert(0, trigFace2) #append would add at the end, and as pop() give you the last element...
                i+=1
            if not(joined):
                quadFaceList.append(trigFace)
        self.faces = quadFaceList
#        if TEST_MODE:
#        print "---"
#        for face in self.faces:
#            print face
#                print self.concaveVertFace(face)




def angle3D(v1, v2,  normal=Vector(0, 0, 1)):
    prodNorm =v1.norm()*v2.norm()
    if prodNorm!=0:
        cos = scalProd(v1, v2)/prodNorm
    else:
        cos = 0
    sign = scalProd(normal, crossProd(v1, v2))
    cos = round(cos, 6)
    if (cos>1) or (cos< -1):
        e.outl(0, "ERROR ANGLE3D")
        return 0
    else:
        theta = math.acos(cos)
    if sign < 0:
        theta = -theta
    return theta

def orientation3D(ab, ad, normal):
    angle = angle3D(ab, ad, normal) # TODO: replace by orientation3D
    if angle>0:
        return 1
    elif angle <0:
        return -1
    else:
        return 0

def orientation(o, a, b):
    oa2  = Vector(-a.y+o.y,a.x-o.x)
    ob    = Vector(b.x-o.x,  b.y-o.y)
    prod = scalProd(oa2,ob)
    if prod > 0:
        return 1
    elif prod == 0:
        return 0
    else:
        return -1
                
def inSector(ab, ad, at,  orienta=1):
    ## Is vector at in the sector defined by the vectors ab and ad?
    o = Vertex(0,0)
    if orientation(o,ab,ad) >= 0:
        inSector =  (orientation(o,ab,at)>=0) and (orientation(o,at,ad)>=0)
    else:
        inSector =  not((orientation(o, ad, at) >= 0) and (orientation(o, at, ab) >= 0))
    ## if counter clockwise:
    if orienta == 1:
        return inSector
    else:
        return not(inSector)
        
def inSector3D(ab, ad, at,  normal, orienta=1):
    ## Is vector at in the sector defined by the vectors ab and ad?
    o = Vertex(0,0)
    if orientation3D(ab,ad, normal) >= 0:
        inSector =  (orientation3D(ab,at, normal)>=0) and (orientation3D(at,ad, normal)>=0)
    else:
        inSector =  not((orientation3D(ad, at, normal) >= 0) and (orientation3D(at, ab, normal) >= 0))
    ## if counter clockwise:
    if orienta == 1:
        return inSector
    else:
        return not(inSector)

        
def intersectLine(a, b, c, t):
    #[c,t] intersects [a,b] ?
    ab=Vector()
    ac= Vector()
    at= Vector()
    ab.vert2vert(a, b)
    ac.vert2vert(a, c)
    at.vert2vert(a, t)
    o= Vertex(0,0)
    if (orientation(a,t,c)>=0):
        return (orientation(a,b,c)!=orientation(a,b,t)) and (orientation(b,a,t)>0) and (orientation(b,c,t)>0)
    else:
        return (orientation(a, b, c) != orientation(a, b, t)) and (orientation(b, a, t) <= 0) and (orientation(b, c, t) <= 0)
        
def intersectLine3D(a, b, c, t, normal):
    #[c,t] intersects [a,b] ?
    ab=Vector()
    ac= Vector()
    at= Vector()
    bt = Vector()
    bc = Vector()
    ab.vert2vert(a, b)
    ac.vert2vert(a, c)
    at.vert2vert(a, t)
    bt.vert2vert(b, t)
    bc.vert2vert(b, c)
    o= Vertex(0,0)
    if (orientation3D(at,ac, normal)>=0):
        return (orientation3D(ab,ac, normal)!=orientation3D(ab,at, normal)) and (orientation3D(-ab,bt, normal)>0) and (orientation3D(bc,bt, normal)>0)
    else:
        return (orientation3D(ab, ac, normal) != orientation3D(ab, at, normal)) and (orientation3D(-ab, bt, normal) <= 0) and (orientation3D(bc, bt, normal) <= 0)

           
def test():        
#    v0 = Vertex(1.4,  0.042957,  -3.428333)
#    v1 = Vertex(1.4,  0.054781,  -2.683436)
#    v2 = Vertex(4.896689,  0.023229,  -3.551223)
#    v3 = Vertex(4.896689,  0.019859,  -3.763519)
#    v4 = Vertex(3.788402,  0.02718, -3.657281)
#    v5 = Vertex(3.788402,  0.028813,  -3.55439)
#    v6 = Vertex(3.788402,  0.031937,  -3.35757)
#    v7 = Vertex(1.440138,  0.047786,  -3.111282)
#    v8 = Vertex(1.440138,  0.042692,  -3.432181)
    
#    v0 = Vertex(4.896689,  0.024849,  -2.883317)
#    v1 = Vertex(4.896689,  0.023229,  -3.551223)
#    v2 = Vertex(1.4,  0.054781,  -2.683436)
#    v3 = Vertex(1.4,  0.060464,  -0.339905)
#    v4 = Vertex(1.59913,  0.058436,  -0.484747)
#    v5 = Vertex(1.59913,  0.058247,  -0.562865)
#    v6 = Vertex(4.845867,  0.025238,  -2.899564)
#    v7 = Vertex(4.845867,  0.025367,  -2.846351)

    v0 = Vertex(0.02200,  -0.48400,  -0.02200)
    v1 = Vertex(0.02200,  -0.49500,  0.00000)
    v2 = Vertex(0.02200,  -0.48400,  0.02200)
    v3 = Vertex(0.02200,  -0.46200,  0.03300)
    v4 = Vertex(0.02200,  -0.44000,  0.02200)
    v5 = Vertex(0.02200,  -0.42900,  0.00000)
    v6 = Vertex(0.02200,  -0.44000,  -0.02200)
    v7 = Vertex(0.02200 -0.46200 -0.03300)

    v0.decal1()
    v1.decal1()
    v2.decal1()
    v3.decal1()
    v4.decal1()
    v5.decal1()
    v6.decal1()
    v7.decal1()
#    v8.decal1()
    
    col = Color(1, 2, 3)
#    normal = Vector(0,  0,  -1)
    normal = Vector(0.008421,  0.999962,  -0.002425)
    normal.decal1()
    normal.cout()
    face = Face()
    face.setNormal(normal)
    face.setColor(col)
    face.setVertices([v0, v1, v2, v3, v4, v5, v6, v7], [0, 1, 2, 3, 4, 5, 6, 7])
    face.createFace(0)
#    poly = Polygon([v0, v1, v2, v3, v4, v5, v6], [0, 1, 2, 3, 4, 5, 6])

def setVertOrder(vertices, vertOrder):
        vertOrder2 = list(vertOrder)
        while len(vertOrder2) > 3:
            for i in range(len(vertOrder2)):
                if isAnEar(vertices, vertOrder2[(i-2)%len(vertOrder2)], vertOrder2[(i-1)%len(vertOrder2)], vertOrder2[i], vertOrder2[(i+1)%len(vertOrder2)], vertOrder2[(i+2)%len(vertOrder2)]):
                    rem = vertOrder2[i]
                    vertOrder2.remove(vertOrder2[i])
                if len(vertOrder2) == 3:
                    break
        # rem is the vertex from which we will connect all the edges
        k = vertOrder.index(rem)
        vertOrder = translateList(vertOrder, k)
        return vertOrder

def pointInTriangle2D(a, b, c, pt):
    #the point pt is inside the triangle abc? only if the segment between pt and (a or b or c) doesn't intersect an other side of the triangle
    return not(intersectLine(a, b, pt, c)) and not(intersectLine(a, c, pt, b)) and not(intersectLine(b, c, pt, a))
 
def pointInTriangle3D(a, b, c, pt):
    u = Vector()
    v = Vector()
    u.vert2vert(a, b)
    v.vert2vert(a, c)
    w = crossProd(u, v)
    base = schmidt(u, v, w)
    u0 = coords(u, base)
    v0 = coords(v, base)
    w0 = coords(w, base)
    u0.z = 0
    v0.z = 0
    w0.z = 0
    return pointInTriangle2D(u0, v0, w0)
    
## ----------- Tree functions -----------------------------

def printTree(tree,  rec=0):
    if rec == 20:
        s = raw_input("\nPAUSE!\n")
    s=""
    for j in range(rec):
        s += "   "
    if tree.sons == []:
        print s+"empty "+str(tree.name) #+ " -> " + str(tree.height) 
    else:
        print s+"node "+str(tree.name)# + " -> " + str(tree.height)
        i = 0
        for node in tree.sons:
            i+=1
            print s+" - node "+str(i)
            printTree(node,  rec+1)

def setHeight (tree,  h=0):
    # Set the height of the nodes, the height of the empty tree is -1
    if tree.sons == []:
        tree.height = h
    else:
        tree.height = h
        for node in tree.sons:
            setHeight(node,  h+1)
            
def breadthFirst (tree):
    # Returns a list of the nodes of the tree after a breadth first search
    l =[]
    lTree = [tree]
    while len(lTree) > 0:
        node = lTree.pop(0)
        l.append(node)
        if node.sons != []:
            for son in node.sons:
                lTree.append(son)
    return l

# ----- List function -------------------

def plusList(l1,  l2):
    l=l1[:] #value copy instead of reference copy
    for i in range(min(len(l), len(l2))):
        l[i]+=l2[i]
    return l
    
def moinsList(l1,  l2):
    l=l1[:] #value copy instead of reference copy
    for i in range(min(len(l), len(l2))):
        l[i]-=l2[i]
    return l
    
def translateList(list, k):
    l2 = []
    for i in range(len(list)):
        l2.append(list[(i+k)%len(list)])
    return l2

# -------------------------------------------

class IPOcurves:
    def __init__(self,  object):
        self.ipo  = Blender.Ipo.New('Object','IPO_'+object.name)
        object.setIpo(self.ipo)
        self.locX = self.ipo.addCurve('LocX')
        self.locY = self.ipo.addCurve('LocY')
        self.locZ = self.ipo.addCurve('LocZ')
        self.rotX = self.ipo.addCurve('RotX')
        self.rotY = self.ipo.addCurve('RotY')
        self.rotZ = self.ipo.addCurve('RotZ')
        self.layer = self.ipo.addCurve('Layer')
        self.locX.setInterpolation('Linear')
        self.locX.setExtrapolation('Constant')
        self.locY.setInterpolation('Linear')
        self.locY.setExtrapolation('Constant')
        self.locZ.setInterpolation('Linear')
        self.locZ.setExtrapolation('Constant')
        self.rotX.setInterpolation('Linear')
        self.rotX.setExtrapolation('Constant')
        self.rotY.setInterpolation('Linear')
        self.rotY.setExtrapolation('Constant')
        self.rotZ.setInterpolation('Linear')
        self.rotZ.setExtrapolation('Constant')
        self.layer.setInterpolation('Linear') # so that next frame != current frame
        self.layer.setExtrapolation('Constant')
        self.frame = 1
        
    def addKey(self, object,  dnmP):
#        print "add Key "+dnmP.name
        if dnmP.CLA == 3:
            self.rotZ.addBezier((1, 0))
            self.rotZ.addBezier((11, 9))
            self.rotZ.setInterpolation('Linear')
            self.rotZ.setExtrapolation("Cyclic_extrapolation")
        if dnmP.CLA > 34:
            e.outl(0, "ERROR: unknown CLA "+str(dnmP.CLA)+" in "+dnmP.name)
            dnmP.CLA = 0
        noAnim = False
        if self.frame == 1:
            #First Frame
            self.frame +=  CLAstartAnim[dnmP.CLA]
            if len(dnmP.STAlist) > 0:
                # with STA, pos = POS+STA
##                y, z, x = plusList(dnmP.POS[:3],  dnmP.STAlist[0][:3])
                y, z, x = dnmP.STAlist[0][:3]
                visib = dnmP.STAlist[0][6]
                # rotation = rotation of POS, composed with rotation of STA in the rotated axis (rotSTA*rotPOS)
##                heading,  pitch,  roll = dnmP.POS[3:6]
##                angles = Angles(-roll, -pitch, heading) # roll = -rotX Blender ; pitch = - rotY Blender ; heading = +rotZ Blender
##                angles.YS2Degree()
##                eulerPOS = Blender.Mathutils.Euler(angles.ax, angles.ay, angles.az)
                heading,  pitch,  roll = dnmP.STAlist[0][3:6]
                angles = Angles(-roll, -pitch, heading) # roll = -rotX Blender ; pitch = - rotY Blender ; heading = +rotZ Blender
                angles.YS2Degree()
##                eulerSTA = Blender.Mathutils.Euler(angles.ax, angles.ay, angles.az)
##                matPOS = eulerPOS.toMatrix()
##                matSTA = eulerSTA.toMatrix()
##                mat = matSTA*matPOS
##                angles = mat.toEuler()
            else:
                noAnim = True
                # no STA
##                y, z, x, heading,  pitch,  roll,  visib = dnmP.POS
##                angles = Angles(-roll, -pitch, heading) # roll = -rotX Blender ; pitch = - rotY Blender ; heading = +rotZ Blender
##                angles.YS2Degree()
##                angles = Blender.Mathutils.Euler(angles.ax, angles.ay, angles.az)
###                visib +=1
            y = -y
        # others frames
        else:
            if (self.frame-1-CLAstartAnim[dnmP.CLA])/animationSTALength <0:
                e.outl(0, "Found a negative index while adding a key :(")
                noAnim = True
            else:
                # next animation frames pos = oldPos+STA[i]
                if len(dnmP.STAlist) > ((self.frame-1-CLAstartAnim[dnmP.CLA])/animationSTALength):
    ##                y, z, x = plusList(dnmP.POS[:3],dnmP.STAlist[(self.frame-1-CLAstartAnim[dnmP.CLA])/animationSTALength][:3])
    #                print self.frame
    #                print dnmP.CLA
    #                print (self.frame-1-CLAstartAnim[dnmP.CLA])/animationSTALength
    #                print dnmP.STAlist[(self.frame-1-CLAstartAnim[dnmP.CLA])/animationSTALength]
    #                print dnmP.STAlist[(self.frame-1-CLAstartAnim[dnmP.CLA])/animationSTALength][:3]
                    y, z, x = dnmP.STAlist[(self.frame-1-CLAstartAnim[dnmP.CLA])/animationSTALength][:3]
                    y = -y
                    visib = dnmP.STAlist[(self.frame-1-CLAstartAnim[dnmP.CLA])/animationSTALength][6]
    ##                heading,  pitch,  roll = dnmP.POS[3:6]
    ##                angles = Angles(-roll, -pitch, heading) # roll = -rotX Blender ; pitch = - rotY Blender ; heading = +rotZ Blender
    ##                angles.YS2Degree()
    ##                eulerPOS = Blender.Mathutils.Euler(angles.ax, angles.ay, angles.az)
                    heading,  pitch,  roll = dnmP.STAlist[(self.frame-1-CLAstartAnim[dnmP.CLA])/animationSTALength][3:6]
                    angles = Angles(-roll, -pitch, heading) # roll = -rotX Blender ; pitch = - rotY Blender ; heading = +rotZ Blender
                    angles.YS2Degree()
    ##                eulerSTA = Blender.Mathutils.Euler(angles.ax, angles.ay, angles.az)
    ##                matPOS = eulerPOS.toMatrix()
    ##                matSTA = eulerSTA.toMatrix()
    ##                mat = matSTA*matPOS
    ##                angles = mat.toEuler()
    
                else:
                    noAnim = True #no STA
                
##        if dnmP.father != "":
##            x -= dnmP.father.CNT[2]
##            y += dnmP.father.CNT[0]
##            z -= dnmP.father.CNT[1]
        # add the current pos
        if noAnim == False:
#            angles = Angles(-roll, -pitch, heading) # roll = -rotX Blender ; pitch = - rotY Blender ; heading = +rotZ Blender
#            angles.YS2Degree()
            # For IPO curves, Blender use degrees/10
            angles.az /= 10.
            angles.ay /= 10.
            angles.ax /= 10.
            if int(visib) == 1:
                layerSTA = 1
                layerPOS = 1
#            elif int(visib) == 1:
#                if int(dnmP.POS[6]) == 0:
#                    layerSTA = 1
#                    layerPOS = 2
#                else:
#                    layerSTA = 2
#                    layerPOS = 1
            else: #0
                layerSTA = 2
                layerPOS = 2
#            print visib, layerPOS,  layerSTA,  int(visib),  int(visib) == 2
            self.locX.addBezier((self.frame, x))
            self.locY.addBezier((self.frame, y))
            self.locZ.addBezier((self.frame, z))
            if dnmP.CLA != 3:            
                self.rotZ.addBezier((self.frame, angles.az))
            self.rotY.addBezier((self.frame, angles.ay))
            self.rotX.addBezier((self.frame, angles.ax))        
            self.layer.addBezier((self.frame, layerSTA))
            self.frame += animationSTALength
#            print x, y, z, angles.ax, angles.ay, angles.az
##            angles2 = Angles(angles.x, angles.y, angles.z) 
##            angles2.degree2Radian()
##            object.LocX = x
##            object.LocY = y
##            object.LocZ = z
##            object.RotZ = angles2.az
##            object.RotY = angles2.ay
##            object.RotX = angles2.ax
##            object.layers = [layerPOS]
   

class ZA:
    def __init__(self,  faceNB, transp=128):
        self.faceNB = faceNB
        self.transp = transp
        
##class ZZ:
##    def __init__(self,  faceNB, transp=128):
##        self.faceNB = faceNB
##        self.transp = transp

class DNMPart:
    """Saving the data from the dnm"""
    def __init__(self,  name="",  fileName="", CNT=[0, 0, 0],  POS=[0, 0, 0, 0, 0, 0, 0],  CLA=0,  STAlist=[],  CLDlist=[]):
        self.name     = name
        self.fileName = fileName
        self.CNT        = CNT
        self.POS        = POS
        self.CLA        = CLA
        self.STAlist    = []
        self.CLDlist    = []        
        self.sons       = []
        self.father     = ""
        height           = 0
        self.ZA= {}
        self.ZZ = {}
        self.ZL = {}




# NOTE about the faces:
# The definition of a face can start with the vertices, the normals, or its color, so createFace() will work only once he got the colors, the normal and the vertices. As we don't know in which order we will get these information, we must try to call createFace() each time we receive one of these information
# That's why I had to create this class
class Face:
    def __init__(self,  material="shadeless"): 
        self.normal      = Vector()
        self.YSnormal  = Vector()
        self.vertices     = []
        self.vertOrder  = []
        self.color         = Color()
        self.gotNormal = False
        self.gotVert     = False
        self.gotColor    = False
        self.bright       = False
        self.number    = 0
        self.is_za      = False
        self.is_zz      = False
        self.is_zl      = False
        self.za        = 0 #transparency level
##        self.zz = 0
        self.material = material
        
#        self.faces = [] # With YS, a face can have more than 4 vertices, so we have to cut the face for Blender
#        self.facesTrig = []
        if TEST_MODE == False:
            self.color=NMesh.Col(0, 0, 0, 0)
    
    def listFaceTrig(self, n):
        l=[]
        i = 2
        prev = 1
        while i <n:
            l.append([0,prev,i])
            prev = i
            i+=1
        return l
      
        
    def calcNormal(self):
        for iFace in self.facesTrig:
            p0 = self.vertices[iFace[0]]
            p1 = self.vertices[iFace[1]]
            p2 = self.vertices[iFace[2]]
            v1 = Vector()
            v2 = Vector()
            v1.vert2vert(p1, p2)
            v2.vert2vert(p1, p0)
            self.normal += crossProd(v1, v2)
            
    def calcTrigNormal(self, iFace):
        if len(iFace) > 2:
            normal = Vector()
            p0 = self.vertices[iFace[0]]
            p1 = self.vertices[iFace[1]]
            p2 = self.vertices[iFace[2]]
            v1 = Vector()
            v2 = Vector()
            v1.vert2vert(p1, p2)
            v2.vert2vert(p1, p0)
            normal += crossProd(v1, v2)
            return normal
        else:
#            e.outl(0, "Could not calculate the normal: a face must have 3 vertices at least")
            return Vector()
            
#    def tesselate(self):
#        #cut the poly into triangles, an put the vertices in the good order
        
    def setBright(self):    
        self.bright = True
        
    def setNormal(self, normal):
        self.YSnormal = normal
        self.gotNormal = True
        
    def setZA(self,  transp,  alpha=0):
        self.is_za = transp
        self.za  = alpha
        
    def setZZ(self,  transp):
        self.is_zz = transp
        
    def setZL(self,  is_zl):
        self.is_zl = is_zl
        
    def setNumber(self, number):
        self.number = number
        
    def setVertices(self, vertices,  vertOrder):
        self.vertices = vertices # All the vertices of the mesh
        self.vertOrder.extend(vertOrder)
        self.gotVert = True
        i = 0
        facesNB =(len(self.vertOrder)-1)/2
        
#        # on enlève les doublons
#        vertOrder2 = []
#        for v in  self.vertOrder:
#            if v in vertOrder2:
#                pass
#            else:
#                vertOrder2.append(v)
#        self.vertOrder = vertOrder2
#        if TEST_MODE == False:
#            while i < facesNB:
#                self.faces.append(NMesh.Face())
#                i+=1
        
    def setColor(self, color):
        self.color = color
        self.gotColor = True
        
    def initialised(self):
        return self.gotColor and self.gotNormal and self.gotVert
        
    def createFace(self, mesh):
        if self.initialised(): # we create a face only if we have received the color information + normal information + vertices information
            # Fix the normal
            poly = Polygon(self.vertices,  self.vertOrder, self.YSnormal)
            # Normal fixed ; Create the face
            if TEST_MODE == False:
                self.color=NMesh.Col(self.color.r, self.color.g, self.color.b, 0)
                for vertsFace in poly.faces:
                    face = NMesh.Face()
                    face.col = [self.color, self.color, self.color, self.color]
                    
                    uv=[]
                    for i in range(len(vertsFace)):
                        uv.append( (0.0,0.0)) 
                    
                    face.uv=uv
                    face.mode^=NMesh.FaceModes['TEX'] 
                    i = 0
                    if self.YSnormal == Vector(0, 0, 0):
                        face.mode|=NMesh.FaceModes['TWOSIDE']
                        
                    if self.bright:
                        face.mode|=NMesh.FaceModes['LIGHT']
                        
                    if self.is_za:
                        face.mode|=NMesh.FaceModes['TEX'] 
                        face.transp|=NMesh.FaceTranspModes['ALPHA']
                        if zatex.hasimage[self.za]:
                            face.image = zatex.image[self.za]
                    if self.is_zz:
                        face.mode|=NMesh.FaceModes['BILLBOARD'] 
##                        face.transp|=NMesh.FaceTranspModes['ALPHA']
##                        if zztex.hasimage[self.zz]:
##                            face.image = zztex.image[self.zz]                            
                    if self.is_zl:
                        face.mode|=NMesh.FaceModes['HALO'] 
                    
                            
                        
#                        face.mode = 513
                    normal = self.calcTrigNormal(vertsFace)
                    # Normal calculation must use triangles
                    if scalProd(self.YSnormal, normal)<0:
                        vertsFace.reverse()
                        vertsFace = translateList(vertsFace, 1)# to keep the same first element in head after the reverse
                    for vert in vertsFace:
                        if i>3:
                            break
                        i+=1
                        face.append(mesh.verts[vert])
                        if self.vertices[vert].round == 1:
                            face.smooth = 1
                    mesh.faces.append(face)
                    
        
class Reader:
    def __init__(self,  material="shadeless"):
        self.material = material
        self.dnmver = 0
        self.init()
        self.maxSTA     = 0
        self.objects       = []
        self.names        = []
        self.packsList    = []
        self.ZAdic         = {}
        self.ZZdic         = {}
        self.ZLdic         = {}
        self.partsList     = []
        self.SRFmeshes = {}
        self.objDic         = {}
        self.ipoDic         = {}
        self.partDic       = {}
        self.dnmProots  = []
        self.faceNB    = 0
            
    def init(self):
        self.face        = Face(self.material)
        self.verts       = []
        self.faceMode = False
        self.faceNB    = 0
        
        if TEST_MODE == False:
            self.mesh=NMesh.GetRaw() 
            self.mesh.hasVertexColours(1)
#            self.mesh.hasFaceUV(1)

    def __del__(self):
        del self.maxSTA 
        del self.objects 
        del self.names
        del self.packsList
        del self.partsList
        del self.SRFmeshes
        del self.objDic
        del self.ipoDic
        del self.partDic
        del self.dnmProots
    
    def move(self, object,  dnmP):
        #print dnmP.name
        try:
            y, z, x, heading,  pitch,  roll,  visib = dnmP.POS
        except:
            y, z, x, heading,  pitch,  roll,  visib = 0, 0, 0, 0, 0, 0, 0
            e.outl(0, dnmP.POS+" is an invalid POS line for "+dnmP.name)
        y = -y
        angles = Angles(-roll, -pitch, heading) # roll = -rotX Blender ; pitch = - rotY Blender ; heading = +rotZ Blender
        angles.YS2Radian()
        if dnmP.father != "":
            # Strange fact, but when you change the CNT, you have to move the children
            x -= dnmP.father.CNT[2]
            y += dnmP.father.CNT[0]
            z -= dnmP.father.CNT[1]
            #print dnmP.father.name,  dnmP.father.CNT[2],  dnmP.father.CNT[0],  dnmP.father.CNT[1]
        object.LocX = x
        object.LocY = y
        object.LocZ = z
        object.RotX = angles.ax
        object.RotY = angles.ay
        object.RotZ = angles.az
    
    def moveObject(self,  dnmP):
        if self.objDic.has_key(dnmP.name):
            obj = self.objDic[dnmP.name]
            self.ipoDic[dnmP.name].addKey(obj,  dnmP)
        else:
            e.outl(0,  "The key "+dnmP.name+" doesn't exists in self.ipoDic")

    
    def setChildren(self,  dnmP, dnmParent):
        ob = self.objDic[dnmP.name]
#        self.moveObject(dnmP)
        objParent = self.objDic[dnmParent.name]
        objParent.makeParent([ob])

    def addMaterial(self):
        if TEST_MODE == False:
            if not self.mesh.materials:
                mat = Blender.Material.New()
                self.mesh.materials.append(mat)
                mat.mode = 0
##                if self.material == "shadeless":
##                    mat.mode |= Blender.Material.Modes['SHADELESS']
                mat.mode |= Blender.Material.Modes['VCOL_PAINT']
                mat.mode |= Blender.Material.Modes['TRACEABLE']
                mat.mode |= Blender.Material.Modes['SHADOWBUF']
                mat.mode |= Blender.Material.Modes['SHADOW']
                mat.mode |= Blender.Material.Modes['ZTRANSP']
                mat.mode |= Blender.Material.Modes['TEXFACE']
                mat.mode |= Blender.Material.Modes['TEXFACE_ALPHA']
#                mat.mode=54591623
#                mat.mode=128

    def createObject(self,  dnmPart=""):
        objectName  = str(dnmPart.name).strip() #make a search and replace for perf
        POS = dnmPart.POS  #make a search and replace for perf
        if TEST_MODE == False:
            #NMesh.PutRaw(self.mesh, objectName) 
            sc = Scene.GetCurrent() 

            ob = None
            scn = bpy.data.scenes.active     # link object to current scene
#            print "dealing with: "+dnmPart.name
            if dnmPart.fileName!="":
                try:
                    ob = scn.objects.new(self.SRFmeshes[dnmPart.fileName], objectName)
                except:
                    e.out("Error, the key "+dnmPart.fileName+"doesn't exist")
            else:
#                ob = scn.objects.new('Empty', objectName)
                mesh = Blender.NMesh.GetRaw()
                mesh.name = "null"
                ob = scn.objects.new(mesh , objectName)
#            ob = scn.objects.new(self.mesh, objectName)
            if ob != None:
                ob.addProperty("CLA", dnmPart.CLA, "INT")
                ob.setDrawType(5)
                ob.layers = [1]
                self.objDic[objectName] = ob
                if len(dnmPart.STAlist) > 0:
                    ipo = IPOcurves(ob) # makes pb because ipo erase pos
                    self.ipoDic[objectName] = ipo
    
                self.objects.append(ob)
                
                self.names.append(objectName)

#            Redraw()

    
    
    def dataSRF(self, line, material="shadeless",  dnmP=None,  lineNB=0):
        if dnmP != None:
            CNT = dnmP.CNT
#            print dnmP.fileName
#            print dnmP.transpFaces
        else:
            CNT = [0, 0, 0]
        e.setLineNB(lineNB)
        data = line.split()
        if len(data)>0: # it's not a blank line
            if ((data[0] == "V") or (data[0] == "VER")) and (self.faceMode==False):
                #importing a vertex
                if data[-1] == "R":
                    try:
                        y, z, x = map(float2, data[1:-1])  # rounded, will have to do a little face.smooth=1 
                    except:
                        e.out("Cannot read the vertex coordinates")
                        y, z, x = 0, 0, 0
                    vertex = Vertex(x-CNT[2], -y+CNT[0], z-CNT[1], 1) # Blender X = z YS ; Blender Y = - x YS ; Blender Z = y YS
                else:
                    try:
                        y, z, x = map(float2, data[1:])      # not rounded
                    except:
                        e.out("Cannot read the vertex coordinates")
                        y, z, x = 0, 0, 0
                    vertex = Vertex(x-CNT[2], -y+CNT[0], z-CNT[1])
                self.verts.append(vertex)
                if TEST_MODE == False:
                    self.mesh.verts.append(NMesh.Vert(x-CNT[2], -y+CNT[0], z-CNT[1]))
                
            elif (data[0] == "F") or (data[0] == "FAC"):
                # Start face section
                self.face = Face(self.material)
                self.faceMode = True
                self.face.setNumber(self.faceNB)
                if dnmP!= None and dnmP.ZA.has_key(self.faceNB):
                    self.face.setZA(True, dnmP.ZA[self.faceNB])
                else:
                    self.face.setZA(False)
                if dnmP!= None and self.faceNB in dnmP.ZZ:
                    self.face.setZZ(True)
                else:
                    self.face.setZZ(False)
                if dnmP!= None and (self.faceNB in dnmP.ZL):
                    self.face.setZL(True)
                else:
                    self.face.setZL(False)
                self.faceNB += 1
                
            elif (data[0] == "C") or (data[0] == "COL"):
                # Color of a face
                col = line.split()
                if len(col) == 2:  #24 bit color conversion
                    rgbCol = Color()
                    try:
                        col = int(col[1])
                        if (col>32767) or (col<0):
                            e.out("24 bits colors must be between 0 and 32767")
                            col = 32767
                    except:
                        e.out("Invalid Color")
                        col = 32767
                    rgbCol.from24b(col)   
                else:                  #RGB
                    try:
                        rgbCol = Color(int(col[1]), int(col[2]), int(col[3]))
                    except:
                        e.out("Invalid colour")
                        rgbCol = Color(255, 255, 255)
                self.face.setColor(rgbCol)
                    
            elif data[0] == "B":
                self.face.setBright()
                    
            elif (data[0] == "N") or (data[0] == "NOR"):
                # Reading Normals and median points
                try:
                    y, z, x = map(float2, data[4:])
                except:
                    e.out("Invalid normal")
                    x, y, z = 0, 0, 0
                normal = Vector(x, -y, z)
                self.face.setNormal(normal)
    
            elif ((data[0] == "V") or (data[0] == "VER")) and (self.faceMode==True):
                # The vertices of the face
                try:
                    vertOrder = map(int, data[1:])
                    # Check a vertID doesn't appear twice, eg 2,4,5,2 -> 2,4,5 else we have problems
                    self.face.setVertices(self.verts, vertOrder)
#                        e.out("a face must have more than 2 vertices")
                except:
                    e.out("Invalid vertOrder")
            elif (data[0] == "E") or (data[0] == "END"):    
                #ends face subsection
                if self.faceMode:
                    self.face.createFace(self.mesh)
                self.faceMode = False
        #self.mesh.update()
                
    def name2Object(self, name):    
        for obj in self.objects:
#            print obj.getName()
            if obj.getName() == name:
#                print "found"
                return obj
        return ""
    
    def readDNM(self, file,  material="shadeless"):
        #---1st read
        fo = open(file, 'r')
        dnmPart = DNMPart()
        totalNBLines = 0
        flagDNMPart = False
        nst = 0
        nch = 0
        while 1:
            text=fo.readline()
            totalNBLines += 1
            if text =="":
                break
            if text[:6] == "DNMVER":
                try:
                    self.dnmver = int(text[7:])
                except:
                    e.outl(totalNBLines, "Invalid DNMVER syntax")
            if text[:3] == "PCK":
                try:
                    self.packsList.append(text.split()[1])
                except:
                    e.outl(totalNBLines, "Invalid PCK syntax")
            if text[:3] == "LIN":
                flagDNMPart = True
                dnmPart = DNMPart()
                try:
                    dnmPart.name = str(text.split()[1]).replace('"','').strip()
                except:
                    e.outl(totalNBLines, "Invalid SRF name syntax")
                #print "LIN "+dnmPart.name
            if text[:3] == "SRF":
                flagDNMPart = True
                dnmPart = DNMPart()
                try:
                    dnmPart.name = str(text[3:]).replace('"','').strip()
                except:
                    e.outl(totalNBLines, "Invalid SRF name syntax")
#                print len(dnmPart.CLDlist)
            if text[:3] == "FIL":
                try:
                    dnmPart.fileName = str(text[3:]).replace('"','').strip()
                    # Attach the ZA line we had read during the PCK inspection
                    if self.ZAdic.has_key(dnmPart.fileName):
                        dnmPart.ZA = self.ZAdic[dnmPart.fileName]
                    if self.ZZdic.has_key(dnmPart.fileName):
                        dnmPart.ZZ = self.ZZdic[dnmPart.fileName]
                    if self.ZLdic.has_key(dnmPart.fileName):
                        dnmPart.ZL = self.ZLdic[dnmPart.fileName]
                except:
                    e.outl(totalNBLines, "Invalid FIL syntax")
            if text[:3] == "CNT":
                try:
                    dnmPart.CNT = map(float2, text.split()[1:])
                except:
                    e.outl(totalNBLines, "Invalid CNT syntax")
            if text[:3] == "POS":
                try:
                    dnmPart.POS = map(float2, text.split()[1:])
                    if len(dnmPart.POS) == 6:
                        dnmPart.POS.append(0)
                    dnmPart.POS = dnmPart.POS[:7]
#                    print dnmPart.name
#                    print dnmPart.POS
                except:
                    e.outl(totalNBLines, "Invalid POS syntax")
#                print dnmPart.POS
            if text[:3] == "CLA":
                try:
                    dnmPart.CLA = int(text.split()[1])
                except:
                    e.outl(totalNBLines, "Invalid CLA syntax")
            if text[:3] == "NST":
                try:
                    nst = int(text.split()[1])
                except:
                    e.outl(totalNBLines, "Invalid NST syntax")
                    nst = 0
                self.maxSTA = max(nst, self.maxSTA)
            if text[:3] == "STA":
                try:
                    dnmPart.STAlist.append(map(float2, text.split()[1:]))
                except:
                    e.outl(totalNBLines, "Invalid STA syntax")
            if text[:3] == "NCH":
                try:
                    nch = int(text.split()[1])
                except:
                    e.outl(totalNBLines, "Invalid NCH syntax")
            if text[:3] == "CLD":
                try:
                    dnmPart.CLDlist.append(str(text[3:]).replace('"','').strip())
                except:
                    e.outl(totalNBLines, "Invalid CLD syntax")
            if text[:2] == "ZA":
                zaList = text[3:].split()
                if len(zaList)%2==1:
                    w.outl(totalNBLines, "Odd number of figures in the ZA line")
                if not(self.ZAdic.has_key(self.packsList[len(self.packsList)-1])):
                     self.ZAdic[self.packsList[len(self.packsList)-1]] = {} 

                for i in range(len(zaList)/2):

                    try:
                        self.ZAdic[self.packsList[len(self.packsList)-1]][int(zaList[2*i])] = int(zaList[2*i+1])
                    except:
                        e.outl(totalNBLines, "Problem reading the ZA line.")
                        
            if text[:2] == "ZZ":
                zzList = text[3:].split()
                if not(self.ZZdic.has_key(self.packsList[len(self.packsList)-1])):
                     self.ZZdic[self.packsList[len(self.packsList)-1]] = [] 

                for i in range(len(zzList)):
                    try:
                        self.ZZdic[self.packsList[len(self.packsList)-1]].append(int(zzList[i]))
                    except:
                        e.outl(totalNBLines, "Problem reading the ZZ line.")
##                if len(zzList)%2==1:
##                    w.outl(totalNBLines, "Odd number of figures in the ZZ line")
##                if not(self.ZZdic.has_key(self.packsList[len(self.packsList)-1])):
##                     self.ZZdic[self.packsList[len(self.packsList)-1]] = {} 
##
##                for i in range(len(zzList)/2):
##
##                    try:
##                        self.ZZdic[self.packsList[len(self.packsList)-1]][int(zzList[2*i])] = int(zzList[2*i+1])
##                    except:
##                        e.outl(totalNBLines, "Problem reading the ZZ line.")
                        
            if text[:2] == "ZL":
                zlList = text[3:].split()
                if not(self.ZLdic.has_key(self.packsList[len(self.packsList)-1])):
                     self.ZLdic[self.packsList[len(self.packsList)-1]] = [] 

                for i in range(len(zlList)):
                    try:
                        self.ZLdic[self.packsList[len(self.packsList)-1]].append(int(zlList[i]))
                    except:
                        e.outl(totalNBLines, "Problem reading the ZL line.")
                    
            if text[:3] == "END":
                if flagDNMPart == True: # Because of the 2nd END final
                    self.partsList.append(dnmPart)
                    while self.partDic.has_key(dnmPart.name):
                        w.outl(0, "Expect troubles, there are 2 SRF called "+dnmPart.name)
                        dnmPart.name+="copy"
                    self.partDic[dnmPart.name]=dnmPart
                    flagDNMPart = False
        fo.close()
#        for dnmP in self.partsList:
#            print dnmP.name
#            print dnmP.POS
        
#        #Check for objects with the same name
#        sortedDnmP = self.partsList[:]
#        sortedDnmP = sorted(sortedDnmP, key=lambda name: name.name)
#        previous = ""
#        for dnmP in sortedDnmP:
#            if dnmP.name == previous:
#                dnmP.name+="copy"
##                for dnmP in self.partsList:
##                    for i in range(len(dnmP.CLDlist)):
##                        if dnmP.CLDlist[i] == previous:
##                            dnmP.CLDlist[i] = previous+"copy"
#                w.outl(0, "Expect troubles, there are 2 SRF called "+previous)
#            else:
#                previous = dnmP.name

    
#        if self.dnmver == 0:
#            # In this case  the first SRF object which doesn't have a father is the parent of all the SRF objects which are not children (else a child could have a father which is also its child)
#            i=0
#            parentFound = False
#            while not(parentFound):
#                parent_of_all = self.partsList[i]
#                parentFound = True
#                for dnmP in self.partsList:
#                    if parent_of_all.name in dnmP.CLDlist:
#                        i+=1
#                        print "not that one"
#                        parentFound = False
#                        break
#                
#            print "Parent of all is "+parent_of_all.name
#            
#            for dnmP in self.partsList:
#                if dnmP != parent_of_all:
#                    parent_of_all.CLDlist.append(dnmP.name)
                
        
            
#        if len(self.packsList) != len(self.partsList):
        dir = os.path.dirname(file)
        for dnmP in self.partsList:
#            print dnmP.fileName
            if dnmP.fileName != "":
#                print "ok"
                if not(dnmP.fileName in self.packsList):
#                    print "this one "+dnmP.fileName
                    # Read an external SRF file
                    self.init()
                    try:
                        fo = open(dir+'/'+dnmP.fileName, 'r')
                    except:
                        e.outl(0, "The file "+dir+'/'+dnmP.fileName+" doesn't exist.")
                    else:
                        self.mesh.name = dnmP.fileName
                        while 1:
                            line=fo.readline()
                            if line=="":
                                break
                            self.dataSRF(line, material,  dnmP)
                        #self.mesh.update(1)
                        fo.close()
                        self.addMaterial()
                        self.SRFmeshes[dnmP.fileName]=self.mesh
        #                    self.createObject(dnmPart)
#                else:
                    
        
        #---2nd read
        fo = open(file, 'r')
        dnmPart= DNMPart() #useful?
        lineNB=0
        objectName = ""
        #name = ""
        Window.RedrawAll()
        noTrouble = True
        while 1:
            if noTrouble:
                text=fo.readline()
            else:
                #print "trouble"
                noTrouble = True
            lineNB += 1
#            if lineNB%30==0:
#                        Window.DrawProgressBar (lineNB/float2(totalNBLines), "Reading DNM data")
            if text =="":
                break
           # if text[:3] == "END":
              #  dnmPart= DNMPart()
                #name = ""
            if text[:3] == "PCK":
                dnmPart= DNMPart()
                srf_line=text.split(" ")
                objectName = srf_line[1]
                log.write("Reading "+objectName)
                flag = False
                for dnmP in self.partsList:
#                    print dnmP.fileName
#                    print dnmP.transpFaces
#                    print "--"
                    if dnmP.fileName ==  objectName:
                        dnmPart = dnmP
                        flag = True
                        break
                if not(flag):
                    w.outl(lineNB,  "the mesh (PCK) "+objectName+" is declared but never used.")
#                print "Importing "+objectName
                lines = srf_line[2]
                read=1
                self.init()    # Clear the faces/vertices of the current object, else we 20 times the same object!
                self.mesh.name = objectName
#                print dnmPart.fileName
#                print dnmPart.transpFaces
                startFace       = False
                foundEndSRF = False
                #print dnmPart.CNT
                while read <= int(lines):
                    line=fo.readline()
                    lineNB += 1
                    if lineNB%30==0:
                        Window.DrawProgressBar (lineNB/float(totalNBLines), "Importing "+objectName)
                    if line=="":
                        break
                    #print line
                    if line[0]=="F" or line[:3]=="FAC":
                        startFace = True
                        #print "true"
                    if line[0]=="E" or line[:3]=="END":
                        if not(startFace):
                            foundEndSRF = True
                            #print "found"
                        else:
                            #print "false"
                            startFace = False
                    self.dataSRF(line,  material,  dnmPart, lineNB)
                    read+=1
                #print "found2"
                #print foundEndSRF
                if not(foundEndSRF):
                    if line != "\r\n" and line != "\n":
                        w.outl(lineNB, "No 'E' or 'END' at the end of the SRF ot wrong line number in PCK")
                    while 1:
                        line=fo.readline()
                        if line=="":
                            break
                        if line[:3] == "PCK" or line[:3]== "SRF":
                            text = line
                            noTrouble = False
                            break
                        lineNB += 1
                        self.dataSRF(line,  material,  dnmPart, lineNB)
                        read+=1
                #print "broke"        
                #self.mesh.update(1)
                self.addMaterial()
                self.SRFmeshes[objectName]=self.mesh # ! objectName = meshName
        
#        #Check for objects with the same name
#        sortedDnmP = self.partsList[:]
#        sortedDnmP = sorted(sortedDnmP, key=lambda name: name.name)
#        previous = ""
#        for dnmP in sortedDnmP:
#            if dnmP.name == previous:
#                dnmP.name+="copy"
##                for dnmP in self.partsList:
##                    for i in range(len(dnmP.CLDlist)):
##                        if dnmP.CLDlist[i] == previous:
##                            dnmP.CLDlist[i] = previous+"copy"
#                w.outl(0, "Expect troubles, there are 2 SRF called "+previous)
#            else:
#                previous = dnmP.name
        
#        # Create the objects
        for dnmP in self.partsList:
#            print dnmP.name
#            print dnmP.POS
            self.createObject(dnmP)


#        print "Imported!"
        fo.close()
            
        
                
        for dnmP in self.partsList:
            for child in dnmP.CLDlist:
                try:
                    dnmP.sons.append(self.partDic[child])
                    self.partDic[child].father = dnmP
                except:
                    e.outl(1,  "Failed to find the object "+child+" declared in the parent tree.")
        

        if self.dnmver == 0:
            # In this case  the first SRF object which doesn't have a father is the parent of all the SRF objects which are not children (else a child could have a father which is also its child)
            i=0
            parentFound = False
            while not(parentFound):
                parent_of_all = self.partsList[i]
                parentFound = True
                for dnmP in self.partsList:
                    if parent_of_all.name in dnmP.CLDlist:
                        i+=1
#                        print "not that one"
                        parentFound = False
                        break
                
#            print "Parent of all is "+parent_of_all.name
            
            for dnmP in self.partsList:
#                if dnmP.father == "":
#                    print dnmP.name,  dnmP.father
#                else:
#                    print dnmP.name,  dnmP.father.name
                if dnmP != parent_of_all and (dnmP.father == "" or dnmP.father==parent_of_all):
#                    print "ok "+dnmP.name
                    parent_of_all.CLDlist.append(dnmP.name)
                    dnmP.father = parent_of_all
                    #self.partDic[dnmP.name].father = parent_of_all
                    if not(dnmP in parent_of_all.sons):
                        parent_of_all.sons.append(dnmP)

            
        if self.dnmver == 0:
            self.dnmProots=[parent_of_all]
        else:
            for dnmP in self.partsList:
                if dnmP.father == "":
                    self.dnmProots.append(dnmP)

#        for dnmP in self.dnmProots:
#            #setHeight(dnmP) #useful??
#            printTree(dnmP)
#            print ("--- next tree ----")
#            s = raw_input("")
         

##        for j in range(self.maxSTA):
        sce = Blender.Scene.GetCurrent()
        for dnmPTree in self.dnmProots:
#            print "root "+dnmPTree.name
            l = breadthFirst(dnmPTree)
            l2 = range(len(l))
            l2.reverse()
            for i in l2:
                dnmP = l[i]
#                print "dealing with "+dnmP.name
                for j in range(len(dnmP.STAlist)):
                    self.moveObject(dnmP)
                empty = Blender.Object.New('Empty')
                empty.name = dnmP.name+"Empty"
                empty.layers = [6]
                sce.objects.link(empty)
                try:
                    empty.makeParent([self.objDic[dnmP.name]])
                except:
                    e.outl(0,"Wrong key, "+dnmP.name+" is not in the dico")
                self.move(empty, dnmP)
                if dnmP.father != "":
                    try:
#                        print dnmP.father.name,  dnmP.name
                        self.objDic[dnmP.father.name].makeParent([empty])
                    except:
                        e.outl(0, "Parent loop problem with "+dnmP.father.name)
##                    self.setChildren(dnmP,  dnmP.father) #we only need to send dnmP!
##                else:
##                    self.moveObject(dnmP)
##                    for j in range(len(dnmP.STAlist)-1):
##                        self.moveObject(dnmP)
            
                    
        Blender.Redraw()
    
    def readSRF(self, file,  material="shadeless", returnObject=False):
        f = open(file, "r") 
        while 1:
            line=f.readline()
            if line=="":
                break
            self.dataSRF(line,  material)
        #self.mesh.update(1)
        f.close()
#        print "Imported!"
        self.addMaterial()
        if TEST_MODE == False:
            sc = Scene.GetCurrent() 
            scn = bpy.data.scenes.active
            slashpos = file.rfind("/") +1
            ob = scn.objects.new(self.mesh, file[slashpos:-4])
#            print self.mesh.materials
            mesh = ob.getData(mesh=1)
#            print mesh.materials
            ob.layers = [1]
            ob.setDrawType(5)
        Blender.Redraw()
        if returnObject:
            return ob
        

def fs_callback2(filename,  material="shademess"):
    fs_callback(filename,  material)
    scn = Scene.GetCurrent()
    diag = 1
    dt = datetime.now()
    date = dt.strftime("%A, %d. %B %Y %I:%M%p")
    if e.errorBuffer != "":
        f=open('errorImportLog.txt','a')
        f.write("\n"+date+"     >>    "+filename[:-4]+"\n")
        f.write(e.errorBuffer)
        f.close()
    if w.warningBuffer != "":
        f=open('warningImportLog.txt','a')
        f.write("\n"+date+"     >>    "+filename[:-4]+"\n")
        f.write(w.warningBuffer)
        f.close()
    e.errorBuffer = ""
    w.warningBuffer = ""
    for ob in scn.objects:
        if ob.type == 'Mesh':
            bb = ob.boundingBox
            x = bb[4].x - bb[0].x
            y = bb[3].y - bb[0].y
            z = bb[1].z - bb[0].z
            diag = max(diag, (x**2+y**2+z**2)**(0.5))
    return diag
 
def fs_callback(filename,  material="shadeless"):
    #Window.Redraw(Window.Types.VIEW3D)
    Window.WaitCursor(1)
    Window.DrawProgressBar (0, "Starting")
    if ( Blender.sys.exists( filename ) == 1 ):
        editmode = Window.EditMode()    # are we in edit mode?  If so ...
        if editmode: 
            Window.EditMode(0) # leave edit mode before getting the mesh
        reader = Reader(material)
#        print ""
        if filename[-3:].lower() == "dnm":
#            print "DNM import version: "+str(__version__)+" - Importing a .DNM"
            reader.readDNM(filename,  material)
        else:
#            print "SRF "+filename+" imported with SRF exporter "+str(__version__)
            reader.readSRF(filename,  material)
        Window.DrawProgressBar (1, "Imported!")
    else:
        Draw.PupMenu( "ERROR: File does not exist!" )
        print filename+'does not exist!'

    scn = Scene.GetCurrent()
    context = scn.getRenderingContext()
    context.fps = animationFPS
    context.sFrame = 0
    context.eFrame = animationEND
    Window.ViewLayers([1])
    obs=[]
    
    for ob in scn.objects:
        if ob.type == 'Mesh':
#            print ob.name
            mesh = ob.getData(mesh=1)
#            mat = Blender.Material.New()
#            mat.mode=54591623
#            mesh.materials.append(mat) 
#            print mesh.materials
            obs.append(ob)
            break
    if len(obs) > 0:
        scn.objects.selected = []
        scn.objects.selected = obs
    Window.WaitCursor(0)
    #print "Check the console, there are "+str(e.errorNB)+" fatal errors which prevented to import properly the file."
    
    #del reader
    
def fs_callback3(filename):
    fs_callback(filename)
    print "errors "+str(e.errorNB)
    if e.errorNB > 0:
        Draw.PupMenu( "Check the console, there are "+str(e.errorNB)+" fatal errors which prevented to import properly the file.")
    log.close()
    
def readSRF(filename):
    reader = Reader("shadeless")
    return reader.readSRF(filename,  "shadeless", True)
        
    
if __name__ =='__main__':
    if TEST_MODE == False:
        Blender.Window.FileSelector(fs_callback3, "Import SRF/DNM")
        
#        fs_callback('/media/echange/g2/ysf//User/Kzs/aircraft.tmb/tmb3kgtn_kz.dnm')
#    fs_callback("/home/vincentweb/b744jal.dnm")
#    fs_callback2("/home/vincentweb/f16.dnm")
#        fs_callback("/home/vincentweb/3D/transpTest.dnm")
#    fs_callback("/home/vincentweb/trend.srf")
#    TEST_MODE = True
#    test()

#else:
#    test()
