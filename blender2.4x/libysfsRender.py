import best_camera_position
reload(best_camera_position)

import ys_render_config
reload(ys_render_config)

import Blender
from Blender.Scene import Render

def extract_path(file):
    # if file = "zd/zde/rtg//lr/mp/file.dnm" we return "/lr/mp/"
    # required to extract the directory where is located a .dnm
    path = ""
    fs1 = file.rfind("//")
    fs2 = file.rfind("/")
    path = file[(fs1+1):(fs2+1)]
    return path


def extract_filename(file):
    # If file = "zd/zde/rtg//lr/mp/file.dnm" we return "file.dnm"
    file = file[:-4]
    fs = file.split("/")
    return fs[len(fs)-1]

def render_path(file, identify, rendermode):
    # According to keep_directory and name_from, we return the path of the file to render
    if ys_render_config.name_from.lower() == "dat":
        identify = remove_chars(identify, ys_render_config.char_to_rem)
        
        if ys_render_config.keep_directory:
            return extract_path(file)+identify+rendermode.extension
        else:
            return extract_path(file)+identify+rendermode.extension
    else:
        file_name = extract_filename(file)
        file_name = remove_chars(file_name, ys_render_config.char_to_rem)
        if ys_render_config.keep_directory:
            return extract_path(file)+extract_filename(file)+rendermode.extension
        else:
            return extract_filename(file)+rendermode.extension
        


def remove_chars(string, chars):
    for char in chars:
        string = string.replace(char,'')
    return string


def render_aircraft(file, render_mode, import_scene, identify):
    sce    = Blender.Scene.GetCurrent()
    #scene  = Scene.New('NewScene')               
    scene = render_mode.scene.copy()
    scene.makeCurrent()
    
##    time1 = time.clock()
    for ob in import_scene.objects:
        if ob.type != "Camera":
            scene.link(ob)
            # Autosmooth
            if ob.getType()=='Mesh': 
                me = ob.getData()
##                print me.mode
                me.mode|=Blender.NMesh.Modes["AUTOSMOOTH"]
                me.setMaxSmoothAngle(80)
                me.update()
##    time2 = time.clock()
##    print "File_______ "+file
##    print "clock: "+str(time2-time1)
    render_mode.world.setCurrent()
    
    
    scn = Blender.Scene.GetCurrent()
    context = scn.getRenderingContext()
    
    # set camera
    camdata      = Blender.Camera.New('persp')
    camdata.name = 'newCam'
    camdata.lens = render_mode.camera_mode.camera_lens
    camera       = scene.objects.new(camdata,'Camera')
    camera.setEuler   (render_mode.camera_mode.camera_angle)
    camera.setLocation(render_mode.camera_mode.location)
    if render_mode.camera_mode.auto_location.lower() != "none":
        calc = best_camera_position.Calculate_Camera_Position(scene)
        calc.calculate_best_position(render_mode.camera_mode.auto_location, render_mode.camera_mode.screen_area, context.sizeX, context.sizeY)

    
    
    # set light
    if render_mode.light_mode.lower() != "none":
        if render_mode.light_mode.lower() == "hemi":
            l = Blender.Lamp.New('Hemi')
        elif render_mode.light_mode.lower() == "sun":
            l = Blender.Lamp.New('Sun')
        elif render_mode.light_mode.lower() == "sun_no_specular":
            l = Blender.Lamp.New('Sun')
            l.setMode('NoSpecular')
        elif render_mode.light_mode.lower() == "hemi_no_specular":
            l = Blender.Lamp.New('Hemi')
            l.setMode('NoSpecular')
        obl = scene.objects.new(l)
        obl.LocZ = 1000
    
    
    
    
    #print render_mode.context.renderPath+extract_filename(file)+render_mode.extension
    #print extract_filename(file)+render_mode.extension
    
    
    #scn.render = render_mode.context
    #render_mode.context = render_mode.scene.render

    Render.EnableDispView()
    
    context.render()
    
    #print render_mode.context.renderPath+extract_filename(file)+render_mode.extension
    
##    print extract_filename(file, ys_render_config.keep_directory)+render_mode.extension
##    render_mode.scene.render.saveRenderedImage(extract_filename(file, ys_render_config.keep_directory)+render_mode.extension)
##    output = extract_filename(file, ys_render_config.keep_directory).replace('/','\\')
    #print render_mode.context.renderPath+extract_filename(file)+render_mode.extension
    ##print file
##    context.renderPath = context.renderPath.replace('\\','/')
    ##print context.renderPath
    ##print output+render_mode.extension
    rendered_file = render_path(file, identify, render_mode)
    context.saveRenderedImage(rendered_file)
    #render_mode.scene.render.saveRenderedImage("file1.jpg")
    #render_mode.scene.render.saveRenderedImage(extract_filename(file, ys_render_config.keep_directory).replace('/','\\')+render_mode.extension)
    
    
    Render.CloseRenderWindow()
    
    scene.unlink(camera)
    sce.makeCurrent() 
    Blender.Scene.Unlink(scene)
    
