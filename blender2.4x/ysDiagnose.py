#!BPY
import glob, os, Blender, hashlib, sys

"""
Name: 'YS Scripts Diagnostic'
Blender: 236
Group: 'System'
Tooltip: 'YSFS Blender scripts Diagnostic tool'
"""

__author__ = "VincentWeb"
__url__ = ("blender", "",
"Author's homepage, http://shadowhunters.yspilots.com")
__version__ = "1"

__bpydoc__ = ""


def md5_for_file(filePath):
    md5 = hashlib.md5()
    file = open(filePath,'rb')
    while True:
        data = file.read(8192)
        if not data:
            break
        md5.update(data)
    file.close()   
    return md5.hexdigest()

# for f in *.py; do echo -n "'$f',"; done; 
# for f in za*.png; do echo -n "'$f',"; done;
# for f in *.py; do m=$(md5sum $f | cut -f 1 -d " "); echo -n "'$m',"; done;

print '------------------ DEBUG START--------------------'
print "OS: ", sys.platform
print "Python Version", sys.version
print "Blender version", Blender.Get('version')
print "Blender home dir", Blender.Get('homedir')
print "Blender script dir", Blender.Get('scriptsdir')
print "Blender user script dir", Blender.Get('uscriptsdir')
print "Working dir:",os.getcwd()

src = ['best_camera_position.py','chza.py','DNMExport.py','dnm_import.py','dnmView.py','libysfsExport.py','libysfs.py','libysfsRender.py','replace_color.py','sce_export.py','sce_import.py','select_by_color.py','show_id.py','show_object.py','show_za.py','SRFExporter.py','unshadow.py','update_gro_list.py','yfs_export.py','ysfsConfig.py','ys_gro_pics.py','ys_hardpoint.py','ysRenderAll2.py','ys_render_config.py']

tex = ['za0.png','za100.png','za101.png','za102.png','za103.png','za104.png','za105.png','za106.png','za107.png','za108.png','za109.png','za10.png','za110.png','za111.png','za112.png','za113.png','za114.png','za115.png','za116.png','za117.png','za118.png','za119.png','za11.png','za120.png','za121.png','za122.png','za123.png','za124.png','za125.png','za126.png','za127.png','za128.png','za129.png','za12.png','za130.png','za131.png','za132.png','za133.png','za134.png','za135.png','za136.png','za137.png','za138.png','za139.png','za13.png','za140.png','za141.png','za142.png','za143.png','za144.png','za145.png','za146.png','za147.png','za148.png','za149.png','za14.png','za150.png','za151.png','za152.png','za153.png','za154.png','za155.png','za156.png','za157.png','za158.png','za159.png','za15.png','za160.png','za161.png','za162.png','za163.png','za164.png','za165.png','za166.png','za167.png','za168.png','za169.png','za16.png','za170.png','za171.png','za172.png','za173.png','za174.png','za175.png','za176.png','za177.png','za178.png','za179.png','za17.png','za180.png','za181.png','za182.png','za183.png','za184.png','za185.png','za186.png','za187.png','za188.png','za189.png','za18.png','za190.png','za191.png','za192.png','za193.png','za194.png','za195.png','za196.png','za197.png','za198.png','za199.png','za19.png','za1.png','za200.png','za201.png','za202.png','za203.png','za204.png','za205.png','za206.png','za207.png','za208.png','za209.png','za20.png','za210.png','za211.png','za212.png','za213.png','za214.png','za215.png','za216.png','za217.png','za218.png','za219.png','za21.png','za220.png','za221.png','za222.png','za223.png','za224.png','za225.png','za226.png','za227.png','za228.png','za229.png','za22.png','za230.png','za231.png','za232.png','za233.png','za234.png','za235.png','za236.png','za237.png','za238.png','za239.png','za23.png','za240.png','za241.png','za242.png','za243.png','za244.png','za245.png','za246.png','za247.png','za248.png','za249.png','za24.png','za250.png','za251.png','za252.png','za253.png','za254.png','za255.png','za256.png','za25.png','za26.png','za27.png','za28.png','za29.png','za2.png','za30.png','za31.png','za32.png','za33.png','za34.png','za35.png','za36.png','za37.png','za38.png','za39.png','za3.png','za40.png','za41.png','za42.png','za43.png','za44.png','za45.png','za46.png','za47.png','za48.png','za49.png','za4.png','za50.png','za51.png','za52.png','za53.png','za54.png','za55.png','za56.png','za57.png','za58.png','za59.png','za5.png','za60.png','za61.png','za62.png','za63.png','za64.png','za65.png','za66.png','za67.png','za68.png','za69.png','za6.png','za70.png','za71.png','za72.png','za73.png','za74.png','za75.png','za76.png','za77.png','za78.png','za79.png','za7.png','za80.png','za81.png','za82.png','za83.png','za84.png','za85.png','za86.png','za87.png','za88.png','za89.png','za8.png','za90.png','za91.png','za92.png','za93.png','za94.png','za95.png','za96.png','za97.png','za98.png','za99.png','za9.png']

md5sum = ['973eb0e77649399b57bc0f740ce2f498','31e14b17f77ed9f805ec4089d4e47271','58b276ad4ad5b67a975a1cfa3dd0fd8f','ac0c253dde19a5d5d059d37be5200e25','71503933b3e6c9ff97a58f3e03a4850a','f6c2eefd645836c06b885a4dcc661b21','287178197d9603a1dad3cd834ac76d3c','77355ab189acd359b15b83f85426046c','eddef2bd315d36b589ec91e5c7b16288','7309b82ec5c5869c043e551ec8f988bd','6638f112fda4ff004788f5f50a9a02d3','4abf09246dcd1a90a5b08cc670ba1856','9985bc220ee0e228a1db84bb6eb97e0f','ce8186d6bb6f1285c95cd09effddc6a2','aff1283f0e4900b3fdd354b1fd104af5','39b770995d2446b9086dcd941ccf0f6a','7e5ba586ef5be5b80d36ecf232ae3559','1273992d6abf00215e4ad8c8bb7bc5b3','66b2dd358dc296e54db124895316aad1','235712a8e6fee2b645470841b6add3f7','69677f431d58102522011719d0e01a3a','b572c8ea9adf281e38afd1d13ceccd1c','93cdd1ef8868fa4b4a9a3fb50de7adb2','47626ee7adcc0003a5904648aacd3a54']

texfiles =  glob.glob(os.path.join(Blender.Get('scriptsdir'),"lib_ysfs/tex/*.png"))
srcfiles =  glob.glob(os.path.join(Blender.Get('scriptsdir'),"*.py"))

texfiles = map (os.path.basename, texfiles)
srcfiles = map (os.path.basename, srcfiles)



if 'ysDiagnose.py' not in srcfiles:
    print "The scripts are supposed to be in", Blender.Get('scriptsdir')
    print "Here there is:"
    print glob.glob(os.path.join(Blender.Get('scriptsdir'), './*'))
else:
    for f in src:
        if f not in srcfiles:
            print f,"is missing in", Blender.Get('scriptsdir')
    for t in tex:
        if t not in texfiles:
            print t, "is missing in", os.path.join(Blender.Get('scriptsdir'),"lib_ysfs/tex")
            print "I break to avoid spamming your command line"
            break
    
    i = 0
    for f in src:
        md5 = md5_for_file(os.path.join(Blender.Get('scriptsdir'),f))
        if md5 != md5sum[i]:
            print f,"is probably corrupted, supposed to have",md5sum[i] ,"but got", md5
        i = i+1
    print "trying to import"
    from ysfsConfig import *
    
print '------------------ DEBUG END--------------------'
