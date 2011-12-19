# -*- coding: iso-8859-1 -*- 

## Common classes and functions to DNMExport, SRFExporter and surf_import
# Script copyright (C) Vincent A. - vincentweb984@hotmail.com

#FIXME: rename calc24b into calc16b
#from ysfsConfig import *
import math
import sys,  time
import Blender
#from Blender import Mathutils

for path in sys.path:
    if path[-17:] == '/.blender/scripts':
        sys.path.append(path+'/blender')

class Log:
    def __init__(self, filename="logYSFS.txt",  turnedON=False):
        self.f = open(filename, "w+")
        self.turnedON = turnedON
        
    def write(self, text):
        if self.turnedON:
            self.f.write(time.strftime("%H:%M:%S: ", time.localtime()) + text + "\r\n")
            self.f.flush()
        
    def close(self):
        self.f.close()

class Error:
    def __init__(self, lineNB=0):
        self.lineNB=lineNB
        self.errorNB = 0
        self.errorBuffer = ""
        
    def setLineNB(self, lineNB):
        self.lineNB=lineNB
        
    def out(self, message):
        self.outl(self.lineNB, message)
        
    def outl(self, lineNB, message):
        print "ERROR line "+str(lineNB)+": " +message
#        self.errorBuffer += "ERROR line "+str(lineNB)+": " +message + "\n"
        self.errorNB+=1
        
class Warning(Error):
    def __init__(self,  lineNB=0):
        Error.__init__(self, lineNB)
        self.warningBuffer = ""
        
    def outl(self, lineNB, message):
        print "WARNING line "+str(lineNB)+": " +message
#        self.warningBuffer += "WARNING line "+str(lineNB)+": " +message + "\n"
        self.errorNB+=1

class Angles:
    """Angle conversions"""
    def __init__(self,  ax,  ay,  az):
        self.ax = ax
        self.ay = ay
        self.az = az
    def degree2Radian(self):
        self.ax *= 0.017453292
        self.ay *= 0.017453292
        self.az *= 0.017453292
    def radian2Degree(self):
        self.ax *= 57.29577951
        self.ay *= 57.29577951
        self.az *= 57.29577951
    def degree2YS(self):
        self.ax = round(self.ax * 182.0444444)
        self.ay = round(self.ay * 182.0444444)
        self.az = round(self.az * 182.0444444)
    def radian2YS(self):
        self.ax = round(self.ax * 10430.37835)
        self.ay = round(self.ay * 10430.37835)
        self.az = round(self.az * 10430.37835)
    def YS2Degree(self):
        self.ax *= 0.005493164
        self.ay *= 0.005493164
        self.az *= 0.005493164
    def YS2Radian(self):
        self.ax *= 0.0000958737992
        self.ay *= 0.0000958737992
        self.az *= 0.0000958737992

    
class Color:
    """Color conversions"""
    def __init__(self, r = 0,  g = 0,  b = 0,  col24 = 0,  brightness = 0): 
        self.r=r
        self.g=g
        self.b=b
        self.col24=col24
        self.brightness = brightness
        
    def calc24b(self):
        self.col24 = self.b/8 + self.r/8*32 + self.g/8*1024
        
    def from24b(self, col24):
        self.col24 = col24
        self.r = 0
        self.g = 0
        self.b = 0
        if col24>1023:
            self.g = col24 / 1024
            col24 -= self.g *1024
        if col24>31:
            self.r = col24 / 32
            col24 -= self.r *32
        self.b = int(col24*255/31.)
        self.g = int(self.g*255/31.)
        self.r = int(self.r*255/31.)
        
    def fromRGB(self, r,  g,  b):
        self.r = r
        self.g = g
        self.b = b
        self.calc24b()
        
    def isEqual2(self,  col):
        return self.r == col.r and self.g == col.g and self.b == col.b and self.col24 == col.col24
        
    def toStr(self): # Print the color
        return str(self.r) +", "+ str(self.g) +", "+ str(self.b) +", "+ str(self.col24) +", "+ str(self.brightness)
        
 
class Vertex(object): 
    def __init__(self, x=0, y=0, z=0,  round=0,  index=0):
       self.x = x
       self.y = y
       self.z = z
       self.round = round
       
    def initList(self,l): # Create a vertex from a list
        self.x = l[0]
        self.y = l[1]
        try:
            self.z = l[2]
        except:
            self.z = 0
            
    def medianPt(self, v1, v2):
        self.x = (v1.x+v2.x)*0.5
        self.y = (v1.y+v2.y)*0.5
        self.z = (v1.z+v2.z)*0.5
            
    def changeBase(self, base):
        x = scalProd(self, base[0])
        y = scalProd(self, base[1])
        try:
            self.z = scalProd(self, base[2])
        except:
            # A 2 vectors base, so a projection
            self.z = 0
        self.x = x
        self.y = y
        
    def distance2(self, v2): # square of the distance of this vertex to an other
        x = v2.x-self.x
        y = v2.y-self.y
        z = v2.z-self.z
        return x*x+y*y+z*z
        
    def decal1(self): # YS coord -> Blender coord
        x = self.x
        y = self.y
        z = self.z
        self.x = z
        self.z = y
        self.y = -x
        
    def decal2(self): # Blender coord -> YS coord
        x = self.x
        y = self.y
        z = self.z
        self.x = -y
        self.y = z
        self.z = x
        
    def copy(self, v):
        self.x = v.x
        self.y = v.y
        self.z = v.z
        
    def plus(self, v): #vp = vp + v
        vp = Vector(self.x+v.x, self.y+v.y, self.z+v.z)
        return vp
        
    def moins(self, v): #vp = vp - v
        vp = Vector(self.x-v.x, self.y-v.y, self.z-v.z)
        return vp
        
    def scal(self, k):
        self.x *= k
        self.y *= k
        self.z *= k
        
    def neg(self):
        return Vertex(-self.x, -self.y, -self.z)
        
    def isEqual2(self, v): # vp == v ?
        return self.x == v.x and self.y == v.y and self.z == v.z
        
    def cout(self): # Print the vertex coordinates
        print(self.x, self.y, self.z)
        
    def toStr(self): # Print the vertex coordinates
        return str(self.x) +", "+ str(self.y) +", "+ str(self.z)
        
    def __eq__(self, v): return (self.x==v.x) and (self.y==v.y) and (self.z == v.z)
        
    def __add__(self, v):  return self.plus(v)
    
    def __sub__(self, v): return self.moins(v)
    
    def __neg__(self): return self.neg()
    
    def rotZ(self,  angle):
        x = math.cos(angle)*self.x-math.sin(angle)*self.y
        y = math.sin(angle)*self.x+math.cos(angle)*self.y
        self.x = x
        self.y = y
    
    def rotY(self,  angle):
        z = math.cos(angle)*self.z-math.sin(angle)*self.x
        x = math.sin(angle)*self.z+math.cos(angle)*self.x
        self.z = z
        self.x = x
        
    def rotX(self,  angle):
        y = math.cos(angle)*self.y-math.sin(angle)*self.z
        z = math.sin(angle)*self.y+math.cos(angle)*self.z
        self.y = y
        self.z = z   
    
 
class Vector(Vertex):        
    def __init__(self, x=0, y=0, z=0):
        super(self.__class__, self).__init__(x, y, z)
        #Vertex.__init__(self, x, y, z)
        
    def pt2pt(self, l1, l2): # Create a vector going from l1 to l2
        self.x = l2[0]-l1[0]
        self.y = l2[1]-l1[1]
        self.z = l2[2]-l2[2]
        
    def vert2vert(self, v1, v2): # Create a vector going from v1 to v2
        self.x = v2.x-v1.x
        self.y = v2.y-v1.y
        self.z = v2.z-v1.z
    
    def normalize(self): # ||v|| = 1
        n = self.norm()
        if n != 0:
            self.x/=n
            self.y/=n
            self.z/=n
        else:
            self.x=0
            self.y=0
            self.z=0
            
    
    def norm(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)


def scalProd(v1,  v2):
    return v1.x*v2.x + v1.y*v2.y + v1.z*v2.z
    
def crossProd(v1,  v2): # v1 /\ v2
    vector = Vector(v1.y*v2.z-v1.z*v2.y, v1.z*v2.x-v1.x*v2.z,  v1.x*v2.y-v1.y*v2.x)
    return vector
    
def nl(): # New Line
    if (sys.platform[:3] == "win") or (sys.platform == "cygwin"):
        return "\n" #the "\r" will be automatically added, else we would get \r\r\n, which is wrong
    else:
        return "\r\n"
    
##def highest(v1, v2):
##    return v1.y<v2.y and v2 or v1
##
##def lowest(v1, v2):
##    return v1.y<v2.y and v1 or v2
##
##def rightmost(v1, v2):
##    return v1.x<v2.x and v2 or v1
##
##def leftmost(v1, v2):
##    return v1.x<v2.x and v1 or v2

#Convert decimal int to binary string
binary = lambda i, c = (lambda i, c: i and (c(i >> 1, c) + str(i & 1)) or ''): c(i, c) 


def float2(s):
    posE = s.find("e")
    if posE != -1:
        posDOT = s.find(".", posE)
        if posDOT != -1:
            s = s[:posDOT]
    return float(s)

class Ztex:
    def __init__(self, mode="za"):
        self.hasimage = []
        self.image    = []
        self.mode     = mode
        self.success   = True # All the pictures are well imported
        self.load_tex()
        
    def load_tex(self):
        for i in range(257):
            try:
                self.image.append(Blender.Image.Load(Blender.Get('scriptsdir')+"/blender/lib_ysfs/tex/"+self.mode+str(i)+".png"))
                self.hasimage.append(True)
            except:
                try:
                    self.image.append(Blender.Image.Load(Blender.Get('scriptsdir')+"/lib_ysfs/tex/"+self.mode+str(i)+".png"))
                    self.hasimage.append(True)
                except:
                    self.hasimage.append(False) # had nothing to do here
                    self.image.append(None)
                    print "Failed to find the picture "+self.mode+str(i)+".png in the folder"+Blender.Get('scriptsdir')+"/blender/lib_ysfs/tex/ and "+Blender.Get('scriptsdir')+"/lib_ysfs/tex/"
                    self.success = False

class Cla:
    def __init__(self, txt, nst):
        self.txt = txt
        self.nst = nst

CLA = {}    
CLA[0]   = Cla("Body or gears", [0,1,2])
CLA[1]   = Cla("Variable geometry wing", [2])
CLA[2]   = Cla("Afterburner", [2])
CLA[3]   = Cla("Propeller", [1]) #why nst=1?
CLA[4]   = Cla("Spoiler", [2])
CLA[5]   = Cla("Flap", [2])
CLA[6]   = Cla("Elevator", [3])
CLA[7]   = Cla("Aileron", [3])
CLA[8]   = Cla("Rudder", [3])
CLA[9]   = Cla("Bomb door", [3]) #why nst=3?
CLA[10] = Cla("Thrust vector (VTOL, nozzles)", [2])
CLA[11] = Cla("Thrust reverser", [2])
CLA[12] = Cla("TV interlock", [2])
CLA[13] = Cla("High speed TV interlock", [2])
CLA[14] = Cla("Gear door", [2])
CLA[15] = Cla("gear casing", [2])
CLA[16] = Cla("Brake/Arresting hook", [2])
CLA[17] = Cla("Gear door 2", [2])
CLA[18] = Cla("Low speed Propeller", [0])
CLA[20] = Cla("High speed Propeller", [0])
CLA[21] = Cla("Auto gun", [3])
CLA[30] = Cla("Nav lights", [2])
CLA[31] = Cla("Strobe lights", [2])
CLA[32] = Cla("Beacon lights", [2])
CLA[33] = Cla("Landing lights", [2])
CLA[34] = Cla("Landing gear lights", [2])

class GEdge:
    def __init__(self, edge, faces):
        self.edge        = edge
        self.faces       = faces
        self.visited    = 0
        
    def copy(self, edge2):
        self.edge = edge2.edge
        self.faces = edge2.faces
        self.visited = edge2.visited
        
class GFace:
    def __init__(self, face, edges):
        self.edges        = edges
        self.face       = face
        self.visited    = 0
        
    def copy(self, edge2):
        self.edges = edge2.edges
        self.face = edge2.face
        self.visited = edge2.visited


def buildEdgesFacesDics(mesh):
    #We use Mesh and not NMesh
    edges = {}
    faces = {}
    for face in mesh.faces:
        if face not in faces:
            faces[face]=GFace(face, [])
        for edge in face.edge_keys:
            if edge not in edges:
                edges[edge] = GEdge(edge, [])
            faces[face].edges.append(edges[edge])
            edges[edge].faces.append(faces[face])
                
    return edges, faces
##    return edges.items()[0][1] #return the first node recorded

def init_visited(edges, faces):
    # remove the visited=1
    if len(edges) > 0:
##        lTree = [edges.items()[0][1]]
        lTree = edges.values()
        while len(lTree) > 0:
            edge = lTree.pop()
            if edge.visited == 1:
                edge.visited = 0
                if edge.faces != []:
                    for face in edge.faces:
                        for edge2 in face.edges:
                            lTree.append(edge2)
                        

def print_keys(edges, faces):
    # remove the visited=1
    init_visited(edges, faces)
    print "-- Print keys -- "
    #lTree = [edges.items()[0][1]]
    lTree = edges.values()
    while len(lTree) > 0:
        edge = lTree.pop()
        if edge.visited == 0:
            print edge.edge
            edge.visited = 1
            for face in edge.faces:
                print "  --> "+str(face.face.index)
                for edge2 in face.edges:
                    lTree.append(edge2)
                    print "   --> "+str(edge2.edge)

def buildBON(w):
    '''Construit la Base Orthonormale Directe (u,v,w)'''
    u = Mathutils.Vector()
    if w.x != 0:
        u.x = -w.y/float(w.x)
        u.y = 1
        u.z = 0
    elif w.y != 0:
        u.y = -w.z/float(w.y)
        u.z = 1
        u.x = 0
    elif w.z != 0:
        u.z = -w.x/float(w.z)
        u.x = 1
        u.y = 0
    v = Mathutils.CrossVecs(w,u)
    u.normalize()
    v.normalize()
    w.normalize()
    return (u,v,w)

def chBaseMat(u,v,w):
    '''Construit la matrice de changement de base P entre la base canonique et (u,v,w)'''
    p = Mathutils.Matrix([u.x, v.x, w.x], [u.y, v.y, w.y], [u.z, v.z, w.z])
    return p.transpose()

def chBase(a, p):
    '''Retourne a dans la base (u,v,w) ou p est les matrice de passage definie par p=chBaseMat(u,v,w)'''
    return p*a

def projPlan(a,p):
    b = chBase(a,p)
    b.resize2D()
    return b

class LineEq:
    def __init__(self):
        self.ax = 0
        self.ay = 0
        self.bx = 0
        self.by = 0
        #t in [0,1]
        
    def getEq(self, x1, y1, x2, y2):
        self.ax = x2 - x1
        self.ay = y2 - y1
        self.bx = x1
        self.by = y1
    
    def getEq2(self, pt,  vect):
        self.getEq(pt.x,  pt.y,  vect.x+pt.x,  vect.y+pt.y)
        
    def __str__(self):
        return "ax: "+str(self.ax)+ " ; ay: "+ str(self.ay)+ " ; bx: "+ str(self.bx) + " ; by: "+ str(self.by)

def intersect(l1, l2):
    det = float(l1.ax * (-l2.ay) + l1.ay * l2.ax)
    if det != 0:
        t1 = ( -(l2.bx - l1.bx)*l2.ay + (l2.by - l1.by)*l2.ax )/det
        t2 = (l1.ax * (l2.by - l1.by) - l1.ay * (l2.bx - l1.bx))/det
        x = l2.ax * t2 + l2.bx
        y = l2.ay * t2 + l2.by
        return Mathutils.Vector(x, y), t1, t2
    else:
        return None, 0
    
def angleNormal(face1, face2, vedge1, vedge2):
    """
    Return the oriented angle between 2 normals
    @type face1: Blender.Mesh.MFace
    @type face2: Blender.Mesh.MFace
    @type edge: Blender.Mathutils.Vector
    @return: The value of the oriented angle between 2 normals
    """
    n1 = face1.no
    n2 = face2.no
    c1 = face1.cent
    c2 = face2.cent
    
    edge = Mathutils.Vector(vedge2.x-vedge1.x, vedge2.y-vedge1.y, vedge2.z-vedge1.z)

    if Mathutils.DotVecs(Mathutils.CrossVecs(n1,n2), edge) < 0:
        edge = -edge
    u,v,w = buildBON(edge)
    p = chBaseMat(u,v,w)
    
    c1 = c1-vedge1 # translation de repere de sortes que le normalize fasse effet sur l1 et l2, cf page 6
    c2 = c2-vedge1
    
    n1p = projPlan(n1,p)
    n2p = projPlan(n2,p)
    c1p = projPlan(c1,p).normalize() # indispensable pour eviter le probleme de la page 6
    c2p = projPlan(c2,p).normalize()
    
    n1p_eq = LineEq()
    n2p_eq = LineEq()
    n1p_eq.getEq2(c1p, n1p)
    n2p_eq.getEq2(c2p, n2p)
    
    print "u,v,w", u,v,w
    print "n1, n2, c1, c2",n1, n2, c1, c2
    print "n1p, n2p, c1p, c2p",n1p, n2p, c1p, c2p
    print "edge",edge
    print "n1p_eq",n1p_eq
    print "n2p_eq",n2p_eq
    
    pt_i, t1, t2 = intersect(n1p_eq, n2p_eq)
    t1,t2 = round(t1,2), round(t2,2)
    
    print "t1,t2",t1, t2
    
    if pt_i != None:
        if t1<=0 and t2<=0:
            return Mathutils.AngleBetweenVecs(n1p,n2p)+180
        elif t1>=0 and t2>=0:
            return 180-Mathutils.AngleBetweenVecs(n2p,n1p)
        else:
            # inconsistent normals
            return 0
    else:
        return 180
    
def angleNormal2(face1, face2, vedge1, vedge2):
    """
    Return the NON oriented angle between 2 normals
    @type face1: Blender.Mesh.MFace
    @type face2: Blender.Mesh.MFace
    @type edge: Blender.Mathutils.Vector
    @return: The value of the NON oriented angle between 2 normals
    """
    n1 = face1.no
    n2 = face2.no
    c1 = face1.cent
    c2 = face2.cent
    
    edge = Mathutils.Vector(vedge2.co.x-vedge1.co.x, vedge2.co.y-vedge1.co.y, vedge2.co.z-vedge1.co.z)

    if Mathutils.DotVecs(Mathutils.CrossVecs(n1,n2), edge) < 0:
        edge = -edge
    u,v,w = buildBON(edge)
    p = chBaseMat(u,v,w)

    
    n1p = projPlan(n1,p)
    n2p = projPlan(n2,p)
    # cf page 7
    try:
        return Mathutils.AngleBetweenVecs(n1p,n2p)
    except:
        print "failed to calculate the angle between faces ", face1.index, " and ", face2.index
##        print "n1=", n1, "  n2p=", n2, "    c1", c1, " c2", c2
##        print "p=", p
##        print "n1p=", n1p, "  n2p=", n2p
        return 0
    
def makeCouples(list):
    """Return the couples which can be made from list"""
    couples = []
    for i in range(len(list)-1):
        for j in range(i+1,len(list)):
           couples.append((list[i],list[j])) 
    return couples

def checkSharpEdges(edges, faces, mesh, maxAngle):
    if len(edges) > 0:
        verts = mesh.verts
        init_visited(edges, faces)
##        print "-- Print keys -- "
##        lTree = [edges.items()[0][1]]
        lTree = edges.values()
        while len(lTree) > 0:
            edge = lTree.pop()
            if edge.visited == 0:
                edge.visited = 1
                couples = makeCouples(edge.faces)
                for couple in couples:
                    face1, face2 = couple
                    v1, v2 = edge.edge
                    if angleNormal2(face1.face, face2.face, verts[v1], verts[v2]) > maxAngle:
##                        print edge.edge, "sharp"
                        irealEdge = mesh.findEdges([edge.edge])
                        realEdge = mesh.edges[irealEdge]
                        realEdge.flag |= Blender.Mesh.EdgeFlags["SHARP"]
                for face in edge.faces:
                    for edge2 in face.edges:
                        lTree.append(edge2)
                    
# ---------- list

def indexMax(list):
    """Return the index of the maximal value of a list"""
    index = 0
    max = list[0]
    for i in range(1, len(list)):
        element = list[i]
        if max < element:
            max = element
            index = i
    return index

def indexLonger(l):
    """
    Return the index of the longest list of the list l
    @type l: a list of lists
    """
    index = 0
    max = len(l[0])
    for i in range(1, len(l)):
        element = len(l[i])
        if max < element:
            max = element
            index = i
    return l[index]

#---------------------------------
def matrixLocalToPos(matrixLocal):
    pos = [0, 0, 0, 0, 0, 0, 0]
    pos[0] = -matrixLocal.translationPart()[1]
    pos[1] = matrixLocal.translationPart()[2]
    pos[2] = matrixLocal.translationPart()[0]

    euler = matrixLocal.rotationPart().toEuler()
    rotAngle2 = Angles(euler.z, -euler.y, -euler.x)
    rotAngle2.degree2YS()
    pos[3] = rotAngle2.ax
    pos[4] = rotAngle2.ay
    pos[5] = rotAngle2.az
    return pos

def obToPos(ob):
    return matrixLocalToPos(ob.matrixLocal)
