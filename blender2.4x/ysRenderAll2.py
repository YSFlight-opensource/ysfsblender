#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'Render all the ys planes 2'
Blender: 236
Group: 'Render'
Tooltip: 'Render all the ys aircraft version 2'
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
        

try: 
    import psyco; psyco.full() 
except: 
    pass

import dnm_import
reload(dnm_import)

import best_camera_position
reload(best_camera_position)

import glob, os, time
import Blender
from Blender import Scene, Object, Lamp
from datetime import datetime
from Blender.Scene import Render

import ys_render_config
reload(ys_render_config)

ys_render_config.ysfs_path=ys_render_config.ysfs_path.replace('\\','/')

# We leave the Edit Mode
editmode = Blender.Window.EditMode()    # are we in edit mode?  If so ...
if editmode: 
    Blender.Window.EditMode(0)

from libysfsRender import *


rendered_files = 0
sce    = Scene.GetCurrent()

if ys_render_config.lst == "any_air":
    regexp = "/aircraft/[Aa][Ii][Rr]*.lst"
elif ys_render_config.lst == "any_gro":
    regexp = "/ground/[Gg][Rr][Oo]*.lst"
else:
    regexp = ys_render_config.lst

dt = datetime.now()    
f4 = open(dt.strftime("rendered_"+"%A, %d. %B %Y %I:%M%p")+".txt", "a")


for air_lst in glob.glob(ys_render_config.ysfs_path+regexp):
    #FIXME: for Linux, files like Air*.lst cannot be detected
    air_lst=air_lst.replace('\\','/')
    f=open(air_lst, 'r')
    while 1:
        text=f.readline()
        if text=="":
            break
        while text.find('.dat')==-1:
            text=f.readline()
            if text=="":
                break
        n_air=text.split()
        if len(n_air)>1 and n_air[0]!="" and n_air[0]!="\n":
##            try:
            file    = ys_render_config.ysfs_path+'/'+n_air[1]
            fileDAT = ys_render_config.ysfs_path+'/'+n_air[0]

            if os.path.exists(file) and os.path.exists(fileDAT):
                if ys_render_config.number_of_files_to_render != -1:
                    if rendered_files >= ys_render_config.number_of_files_to_render:
                        break
                identify = ""
                f3 = open(fileDAT, "r")
                while 1:
                    text = f3.readline()
                    if text == "":
                        break
                    if len(text)>8:
                        if text[:8].upper() == "IDENTIFY":
                            identify = text[8:].strip().replace('\"','')
##                            print identify
                need_render = False
                need_render_d = {}
                j = 0
                for render in ys_render_config.render_modes:
                    j += 1
                    render_mode = ys_render_config.render_modes[render]
                    
                    rendered_file = render_mode.scene.render.renderPath+render_path(file, identify, render_mode)
                    f4.write("[pic"+str(j)+"]"+rendered_file+"[/pic"+str(j)+"]\n")
                    print rendered_file
                        
                    if ys_render_config.override or not(os.path.exists(rendered_file)):
                        need_render = True
                        need_render_d[render]=True
                        #render_aircraft(file, render_mode, import_scene)
                    else:
                        need_render_d[render]=False
                f4.write("\n")
                if need_render:
                    if os.path.exists(file) and os.path.isfile(file):
##                        print "rendering: "+file
                        import_scene = Scene.New('importScene')
                        import_scene.makeCurrent()
##                        print file
                        #s=raw_input("")
                        try:
                            #print "importation disabled!"
                            diag = dnm_import.fs_callback2(file, ys_render_config.material)
                        except:
                            print "Failed to import "+file
                            dt = datetime.now()
                            date = dt.strftime("%A, %d. %B %Y %I:%M%p")
                            f2=open('errorImportLog.txt','a')
                            f2.write("\n"+date+"     >>    "+file+"\n")
                            f2.write("!!!!!!!!!!!!!!!!!!!!!!!\r\n")
                            f2.write("FAILED TO IMPORT")
                            f2.write("!!!!!!!!!!!!!!!!!!!!!!!\r\n")
                            f2.close()
                        else:
                            rendered_files += 1
                            for render in ys_render_config.render_modes:
                                if need_render_d[render]:
                                    render_mode = ys_render_config.render_modes[render]
                                    render_aircraft(file, render_mode, import_scene, identify)
                                    
                            sce.makeCurrent()
                            Scene.Unlink(import_scene)
                    else:
                        print file+" or "+fileDAT+" isn't a file."
            
            else:
                print file + " or "+fileDAT+" does not exists."
##            except:
##                print "problem with " + n_air[1]
            
            
            
    f.close()    

print "Error log, Warning log, list of rendered pictures saved in "+os.getcwd()