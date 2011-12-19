##############################################################################################"
##             Class definitions, you can set your configuration below "Configuration"
##                       DO NOT MODIFY THE CODE ABOVE "Configuration"
##############################################################################################"


import Blender
from Blender.Mathutils import *

render_modes = {}

class Camera_Mode:
    def __init__(self, location, camera_angle, camera_lens, auto_location, screen_area):
        self.location       = location       # Position of the camera, useful for setting the location of the camera manually, eg Vector(0,0,100), else it's useless except if you set autolocation=none
        self.camera_angle   = camera_angle   # Angle/orientation of the camera, eg Euler(1.57, 0, 3.14)
        self.camera_lens    = camera_lens    # Lens/zoom of the camera, eg 35
        self.auto_location  = auto_location  # Choose here the method to calculate the position of the camera, accepted values: "auto", "face_median_pts"
        self.screen_area    = screen_area    # Area of the screen to use, between 0 and 100 percent, you can use higher values to zoom
        


class Render_Mode:
    def __init__(self, scene, camera_mode, world, light_mode, extension):
        self.scene        = scene            # Scene, contains the rendering context (render path, image type, oversampling, size...)
        self.camera_mode  = camera_mode      # Contains a Camera_Mode object (which contains the camera location, the camera angle, the camera lens ...)
        self.world        = world            # Contains a World object (background, sky type, stars, ...)
        self.light_mode   = light_mode       # Select the light mode, can be "none", "hemi", "hemi_no_specular", "sun", "sun_no_specular", useless if material="shadeless" (see below, in this case choose light_mode="none")
        self.extension    = extension        # Chose here the extension of the rendered pictures, can be ".jpg", ".png", ... "_my_render.jpg", "_large_render.png", ...



#############################################################"
##             CONFIGURATION, here you can modify stuff
#############################################################"


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!! WINDOWS USERS: REPLACE '\' by "\\" !!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Path of your YSFlight installation
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!! Windows: DON'T FORGET the "\\" AT THE END OF THE PATH   -   Linux: DON'T FORGET THE "/" AT THE END OF THE PATH     !!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ysfs_path = "E:\\progs\\ysf2\\"
##ysfs_path = "/media/echange/g2/ysf/"


# Characters to remove of the name of the rendered picture
# With the default configuration, if the script is about to save the rendered picture 'f-16_<my_squad>.jpg', the script will rather call the picture 'f-16_my_squad.jpg'
char_to_rem = ['*', '\"', '/', ':', '?', "<", ">", "|"]

# Choose here the lst to use:
# lst = "any_air" will load all the lst of the kind air*.lst
# lst = "any_gro" will load all the lst of the kind gro*.lst
# lst = "\\aircraft\\air_my_pack.lst" or lst = "/ground/gro_my_pack.lst" will only load air_my_pack.lst, gro_my_pack.lst respectively
lst = "any_air"

# The generated pictures can have the name of the IDENTIFY in the .dat or the name of the .dnm
# If you choose "dnm" and the script is rendering aircraft/f16.dnm, the rendered picture will be called f16.jpg
# If you choose "dat" and the script is rendering aircraft/f16.dnm, the rendered picture will be called F-16C_FIGHTINGFALCON.jpg (name from the .dat)
name_from = "dat"

# Number of files to render, the script will stop after "number_of_files_to_render" rendered
# Number of files to render, the script will stop after "number_of_files_to_render" rendered
number_of_files_to_render = -1

# If we are about to render a picture with the same name, shall we override the old file?
# Letting this option to False enables to "resume" the render of your files
override = False

# keep_directory = True  -> put the rendered pictures in folders with the same name of the one containing the original files
# keep_directory = False -> put all the rendered pictures in the same directory
keep_directory = True

# Choose the material of the objects between "shadeless" and "normal"
material = "normal"

# We define here the different renders we do

# Our first render will generate a thumbnail
scene1  = Blender.Scene.New('NewScene1')               # We create a scene

world   = Blender.World.Get('World')                   # We load the world "World"
context = scene1.getRenderingContext()
context.imageType    = Blender.Scene.Render.JPEG       # We use the jpeg format
context.renderPath = "E:\\progs\ysf2\\renders\\"       # Path where to put our rendered pictures
##context.renderPath = "/home/vincentweb/3D/blender/render/ysRenders/gro/"
context.oversampling = True                            # Antialiasing is ON
context.OSALevel     = 8                               # Anitialiasing level = 8
context.sizeX        = 140                             # Rendered picture width
context.sizeY        = 110                             # Rendered picture height, it's small because it's a thumbnail
# We define the paramateres of the camera:
#     Its initial position before to calculate its optimal position is (0, 0, 20)
#     The angle of the camera is (rotX = 1.22173, rotY = 0, rotZ = 0.610865)
#     The lens of the camera is 35 (for the focal length)
#     The calculation method of the position of the camera is "auto"
#     The area of the screen to use is 95%
camera_mode1 = Camera_Mode(Vector(0, 0, 20), Euler(1.22173, 0, 0.610865), 35, "auto", 95)
# We define the parameters of the first render which will create the thumbnail picture:
#    The scene is scene1
#    The camera mode is camera_mode1
#    The world is world (Blender.World.Get('World'))
#    The light is "hemi_no_specular"
#    The extension of the rendered file is "_thumbnail.jpg"
render_mode1 = Render_Mode(scene1, camera_mode1, world, "hemi_no_specular", "_thumbnail.jpg")
render_modes["thumbnail"] = render_mode1             # We had the render mode in the dictionary

# Our second render will generate a larger picture
scene2  = Blender.Scene.New('NewScene2')
context = scene2.getRenderingContext()
context.imageType    = Blender.Scene.Render.JPEG
context.renderPath = "E:\\progs\\ysf2\\renders\\"
##context.renderPath = "/home/vincentweb/3D/blender/render/ysRenders/gro/"
context.currentFrame(41)                    # we will render the frame 41, at that frame we can see the gears down ...
context.oversampling = True
context.OSALevel     = 8
context.sizeX        = 800
context.sizeY        = 600
camera_mode2 = Camera_Mode(Vector(40, -40, 12), Euler(1.22173, 0, 0.610865), 35, "face_median_pts", 70)
render_mode2 = Render_Mode(scene2, camera_mode2, world, "hemi_no_specular", "_large.jpg")
render_modes["large_pic"] = render_mode2
