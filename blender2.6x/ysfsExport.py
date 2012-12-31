# -*- coding: utf-8 -*-

import mathutils
import bpy

from ysfs_lib.srfExport import Mesh, MeshWriter

# We take an inventory of all the meshes in meshDic 
# to avoid writting them several times

meshDic = {}

fd = open("test.srf", "w")

def mesh2ysfs(ob):
    mesh = ob.data
    if mesh.name not in meshDic:
        meshDic[mesh.name] = True
        m          = Mesh(mesh)
        meshWriter = MeshWriter(m, fd)
        meshWriter.write()
        
        
        

def obj2ysfs(ob):
    if ob.type == 'MESH':
        mesh2ysfs(ob)
        
global_undo = bpy.context.user_preferences.edit.use_global_undo
bpy.context.user_preferences.edit.use_global_undo = False

scene = bpy.context.scene
for ob in scene.objects:
    obj2ysfs(ob)

fd.close()
bpy.context.user_preferences.edit.use_global_undo = global_undo