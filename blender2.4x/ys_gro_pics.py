#!BPY
# -*- coding: iso-8859-1 -*- 


"""
Name: 'Generate thumbnails of all the ground objects'
Blender: 236
Group: 'Render'
Tooltip: 'Generate thumnails of all the ground objects'
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





import glob, os, time
import Blender
from Blender import Scene, Object, Lamp
from datetime import datetime
from Blender.Scene import Render
from Blender.Mathutils import *

import libysfsRender
reload(libysfsRender)

import ys_render_config
reload(ys_render_config)

#----- config

ys_render_config.ysfs_path = "/media/echange/g2/ysf/"#"/home/vincentweb/ysflight/"

ys_render_config.render_modes = {}
ys_render_config.material = "normal"
scene1  = Blender.Scene.New('NewScene1')               # We create a scene

world   = Blender.World.Get('World')                   # We load the world "World"
context = scene1.getRenderingContext()
context.imageType    = Blender.Scene.Render.JPEG       # We use the jpeg format
context.renderPath = "/var/www/grounds/"       # Path where to put our rendered pictures
context.oversampling = True                            # Antialiasing is ON
context.OSALevel     = 8                               # Anitialiasing level = 8
context.sizeX        = 140                             # Rendered picture width
context.sizeY        = 110                             # Rendered picture height, it's small because it's a thumbnail

camera_mode1 = ys_render_config.Camera_Mode(Vector(0, 0, 20), Euler(1.22173, 0, 0.610865), 35, "auto", 95)

render_mode1 = ys_render_config.Render_Mode(scene1, camera_mode1, world, "hemi_no_specular", "_thumbnail.jpg")
ys_render_config.render_modes["thumbnail"] = render_mode1



#----- end config


ys_render_config.ysfs_path=ys_render_config.ysfs_path.replace('\\','/')

# We leave the Edit Mode
editmode = Blender.Window.EditMode()    # are we in edit mode?  If so ...
if editmode: 
    Blender.Window.EditMode(0)




rendered_files = 0
sce    = Scene.GetCurrent()

regexp = "/ground/[Gg][Rr][Oo]*.lst"


dt = datetime.now()    
f4 = open(ys_render_config.render_modes["thumbnail"].scene.getRenderingContext().renderPath+"/grounds_all_1.htm", "w")
f4_aaa = open(ys_render_config.render_modes["thumbnail"].scene.getRenderingContext().renderPath+"/grounds_aaa_1.htm", "w")
f4_sam = open(ys_render_config.render_modes["thumbnail"].scene.getRenderingContext().renderPath+"/grounds_sam_1.htm", "w")
f4_can = open(ys_render_config.render_modes["thumbnail"].scene.getRenderingContext().renderPath+"/grounds_can_1.htm", "w")

f4.write('<a href="grounds_all_1.htm">all ground objects</a> &nbsp;|&nbsp; <a href="grounds_aaa_1.htm">ground objects with gun</a> &nbsp;|&nbsp; <a href="grounds_sam.htm">ground objects with missiles </a> &nbsp;|&nbsp; <a href="grounds_can_1.htm">ground objects with canon</a>')
f4_aaa.write('<a href="grounds_all_1.htm">all ground objects</a> &nbsp;|&nbsp; <a href="grounds_aaa_1.htm">ground objects with gun</a> &nbsp;|&nbsp; <a href="grounds_sam_1.htm">ground objects with missiles </a> &nbsp;|&nbsp; <a href="grounds_can_1.htm">ground objects with canon</a>')
f4_sam.write('<a href="grounds_all_1.htm">all ground objects</a> &nbsp;|&nbsp; <a href="grounds_aaa_1.htm">ground objects with gun</a> &nbsp;|&nbsp; <a href="grounds_sam_1.htm">ground objects with missiles </a> &nbsp;|&nbsp; <a href="grounds_can_1.htm">ground objects with canon</a>')
f4_can.write('<a href="grounds_all_1.htm">all ground objects</a> &nbsp;|&nbsp; <a href="grounds_aaa_1.htm">ground objects with gun</a> &nbsp;|&nbsp; <a href="grounds_sam_1.htm">ground objects with missiles </a> &nbsp;|&nbsp; <a href="grounds_can_1.htm">ground objects with canon</a>')

def extract_option(var, option):
    if len(text)>len(option):
        if text[:len(option)].upper() == option:
            return text[len(option):].strip().replace('\"','')
    return var

def int2(str):
    try:
        return int(str)
    except:
        return 0
    
def cutstr(str):
    s = ""
    for i in range(len(str)):
        s+=str[i]
        if i%14==13:
            s+="<br>"
    return s

def add_page(f, page, nb, name, lst):
    if nb/page > 200:
        f.write("</tr></table>")
        f.write("<br><br>")
        if page>1:
            f.write("<a href='"+name+"_"+str(page-1)+".htm'>&lt;--- previous &nbsp;</a>|")
        f.write("<a href='"+name+"_"+str(page+1)+".htm'>&nbsp; next ---&gt;</a>")
        f.close()
        page+=1
        f = open(ys_render_config.render_modes["thumbnail"].scene.getRenderingContext().renderPath+"/"+name+"_"+str(page)+".htm", "w")
        f.write('<br><br><big style="text-decoration: underline; font-weight: bold;">'+libysfsRender.extract_filename(lst)+'</big>\n<table><tr>')
    return f, page
  
nb_all = 0
nb_aaa = 0
nb_sam = 0
nb_can = 0

page_all = 1
page_aaa = 1
page_sam = 1
page_can = 1  

for air_lst in glob.glob(ys_render_config.ysfs_path+regexp):
    #FIXME: for Linux, files like Air*.lst cannot be detected
    air_lst=air_lst.replace('\\','/')
    f=open(air_lst, 'r')
    
    j=0
    jaaa=0
    jsam=0
    jcan=0

    
    
    
    
    
    f4.write('<br><br><big style="text-decoration: underline; font-weight: bold;">'+libysfsRender.extract_filename(air_lst)+'</big>\n<table><tr>')
    f4_aaa.write('<br><br><big style="text-decoration: underline; font-weight: bold;">'+libysfsRender.extract_filename(air_lst)+'</big>\n<table><tr>')
    f4_sam.write('<br><br><big style="text-decoration: underline; font-weight: bold;">'+libysfsRender.extract_filename(air_lst)+'</big>\n<table><tr>')
    f4_can.write('<br><br><big style="text-decoration: underline; font-weight: bold;">'+libysfsRender.extract_filename(air_lst)+'</big>\n<table><tr>')
    
##    print "--->",air_lst
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
##            print n_air
            file    = ys_render_config.ysfs_path+'/'+n_air[1]
            fileDAT = ys_render_config.ysfs_path+'/'+n_air[0]
##            print file
            if os.path.exists(file) and os.path.exists(fileDAT):
                if ys_render_config.number_of_files_to_render != -1:
                    if rendered_files >= ys_render_config.number_of_files_to_render:
                        break
                identify = ""
                htradius = ""
                strength = 0
                initigun = 0
                initcano = 0
                initisam = 0
                maxspeed = ""
                gunrange = ""
                canrange = ""
                samrange = ""
                grndtype = ""
                f3 = open(fileDAT, "r")
                while 1:
                    text = f3.readline()
                    if text == "":
                        break
                    identify = extract_option(identify, "IDENTIFY")
                    htradius = extract_option(htradius, "HTRADIUS")
                    strength = int2(extract_option(strength, "STRENGTH"))
                    initigun = int2(extract_option(initigun, "INITIGUN"))
                    initcano = int2(extract_option(initcano, "INITCANO"))
                    initisam = int2(extract_option(initisam, "INITISAM"))
                    maxspeed = extract_option(maxspeed, "MAXSPEED")
                    gunrange = extract_option(gunrange, "GUNRANGE")
                    canrange = extract_option(canrange, "CANRANGE")
                    samrange = extract_option(samrange, "SAMRANGE")
                    grndtype = extract_option(grndtype, "GRNDTYPE")
                need_render = False
                need_render_d = {}
                for render in ys_render_config.render_modes:
                    j += 1
                    nb_all +=1
                    f4, page_all = add_page(f4, page_all, nb_all, "grounds_all", air_lst)
                    render_mode = ys_render_config.render_modes[render]
                    print "identify", identify, j
                    rfile = libysfsRender.render_path(file, identify, render_mode)
                    rendered_file = render_mode.scene.render.renderPath+rfile
                    rfile2 = rfile
                    if rfile2[0] == "/":
                        rfile2 = rfile2[1:]
                    buffer = """
<td>
<table style="text-align: left; width: 164px;" border="0"
 cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td valign="top"><img
 style="border: 1px solid ; width: 140px; height: 110px;" alt="thumbnail"
 src='"""+rfile2+"""'></td>
    </tr>
    <tr>
      <td valign="top"><span style="font-weight: bold;">"""+cutstr(identify)+"""</span><br>
      <small>"""+grndtype+"""</small><br>
      <small><img style="width: 15px; height: 15px;"
 alt="size"
 src="im/size.png"> """+htradius+""" <img style="width: 15px; height: 15px;" alt="strength"
src="im/hammer.png"> """+str(strength)+""" &nbsp;<img style="width: 15px; height: 15px;"
 alt="speed"
 src="im/speed.png">
"""+maxspeed+"""<br>
&nbsp;"""
                    if initigun != 0:
                        jaaa+=1
                        nb_aaa +=1
                        f4_aaa, page_aaaa = add_page(f4_aaa, page_aaa, nb_aaa, "grounds_aaa", air_lst)
                        buffer += """<img style="width: 15px; height: 15px;" alt="gun"
 src="im/aaa.png">
"""+str(initigun)+"""-"""+gunrange+""" &nbsp; <br>"""
                    if initisam != 0:
                        jsam+=1
                        nb_sam +=1
                        f4_sam, page_sam = add_page(f4_sam, page_sam, nb_sam, "grounds_sam", air_lst)
                        buffer += """<img style="width: 15px; height: 15px;" alt="missile"
 src="im/missile.png">
"""+str(initisam)+"""-"""+samrange+""" <br>"""

                    if initcano != 0:
                        jcan+=1
                        nb_can+=1
                        f4_can, page_can = add_page(f4_can, page_can, nb_can, "grounds_can", air_lst)
                        buffer += """<img style="width: 15px; height: 15px;" alt="canon"
 src="im/canon.png">
"""+str(initcano)+"""-"""+canrange+"""</small>"""

                    buffer +="""</td>
    </tr>
  </tbody>
</table>
</td>
"""
                    
                    f4.write(buffer)
                    
                    if initigun != 0:
                        f4_aaa.write(buffer)
                        
                    if initisam != 0:
                        f4_sam.write(buffer)
                        
                    if initcano != 0:
                        f4_can.write(buffer)
                        
                    if j%5 == 0:
                        f4.write("</tr><tr>")
                        
                    if jaaa%5 == 0:
                        f4_aaa.write("</tr><tr>")
                        
                    if jsam%5 == 0:
                        f4_sam.write("</tr><tr>")
                        
                    if jcan%5 == 0:
                        f4_can.write("</tr><tr>")
                        
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
                                    libysfsRender.render_aircraft(file, render_mode, import_scene, identify)
                                    
                            sce.makeCurrent()
                            Scene.Unlink(import_scene)
                    else:
                        print file+" or "+fileDAT+" isn't a file."
            
            else:
                print file + " or "+fileDAT+" does not exists."
##            except:
##                print "problem with " + n_air[1]
            
            
    f4.write("</tr></table>")
    f4_aaa.write("</tr></table>")
    f4_sam.write("</tr></table>")
    f4_can.write("</tr></table>")
    
f4.write("<a href='grounds_all_"+str(page_all-1)+".htm'>&lt;--- previous &nbsp;</a>")
f4_aaa.write("<a href='grounds_aaa_"+str(page_aaa-1)+".htm'>&lt;--- previous &nbsp;</a>")
f4_sam.write("<a href='grounds_sam_"+str(page_sam-1)+".htm'>&lt;--- previous &nbsp;</a>")
f4_can.write("<a href='grounds_can_"+str(page_can-1)+".htm'>&lt;--- previous &nbsp;</a>")

f4.close()    
f4_aaa.close()
f4_sam.close()
f4_can.close()

print "Error log, Warning log, list of rendered pictures saved in "+os.getcwd()