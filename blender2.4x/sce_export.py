#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'Scenary (.fld)'
Blender: 236
Group: 'Export'
Tooltip: 'Export the objects layout of an YSFlight scenary in the fld format'
"""


__author__ = "VincentWeb"
__url__ = ("blender", "",
"Author's homepage, http://shadowhunters.yspilots.com")
__version__ = "0.1"

__bpydoc__ = """\
"""


import sys

for path in sys.path:
    if path[-17:] == '/.blender/scripts':
        sys.path.append(path+'/blender')
        

import Blender
import dnm_import
reload(dnm_import)

from libysfs import *

e = Error()

        
def write_fld(filename):
    out = file(filename, 'w')
    out.write('FIELD'+nl())
    sce = Blender.Scene.GetCurrent()
    objects = sce.objects
    for ob in objects:
        if ob.getType() == 'Mesh':
            out.write('GOB'+nl())
            angles = Angles(ob.RotZ, -ob.RotY, -ob.RotX)
            angles.radian2YS()
            out.write('POS %.4f %.4f %.4f %.4f %.4f %.4f' % (-ob.LocY, ob.LocZ, ob.LocX, angles.ax, angles.ay, angles.az))
            out.write(nl())
            try:
                out.write('ID '+str(ob.getProperty("ID").getData())+nl())
            except:
                out.write('ID 0'+nl())
            try:
                out.write('NAM '+str(ob.getProperty("NAM").getData())+nl())
            except:
                name = ob.name.upper()
                pos = name.find(".")
                if pos != -1:
                    name = name[:pos]
                out.write('NAM '+name+nl())
            try:
                out.write('IFF '+str(ob.getProperty("IFF").getData())+nl())
            except:
                out.write('IFF 0'+nl())
            try:
                out.write('FLG '+str(ob.getProperty("FLG").getData())+nl())
            except:
                out.write('FLG 0'+nl())
            out.write('END'+nl())
            
    out.write('ENDF'+nl())
    
Blender.Window.FileSelector(write_fld, "Export a .fld scene",   Blender.sys.makename(ext='.fld'))