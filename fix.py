"""
I use this script to 'upgrade' and check some old app...
"""

import glob, os, sys, urllib, simplejson

def cleanup():    
    os.system("rm */sessions/*")
    os.system("rm */errors/*")
    os.system("rm */databases/*")
    os.system("rm */cache/*")
    os.system("rm */uploads/*")
    os.system("rm */private/*")
    os.system("rm -r models views controllers cache errors sessions uploads static ABOUT LICENSE tests cron modules languages databases private")
    
    os.system("find ./ -name '*~' -exec rm -f {} \; ")
    os.system("find ./ -name '*.orig' -exec rm -f {} \;") 
    os.system("find ./ -name '*.rej' -exec rm -f {} \; ")
    os.system("find ./ -name '*.bak' -exec rm -f {} \; ")
    os.system("find ./ -name '*.bak2' -exec rm -f {} \; ")
    os.system("find ./ -name '*.pyc' -exec rm -f {} \; ")
    os.system("find ./ -name '*.pyo' -exec rm -f {} \; ")
    os.system("find ./ -name '*.log' -exec rm -f {} \; ")
    os.system("find ./ -name '*.1' -exec rm -f {} \; ")
    os.system("find ./ -name '#*' -exec rm -f {} \;")

def fixoldsyntax():
    files = glob.glob('*/modules/*.py') + glob.glob('*/controllers/*.py') + glob.glob('*/views/*.html') + glob.glob('*/views/*/*.html')
    for f in files:
        data=open(f).read()
        data = data.replace('SQLDB','DAL')
        data = data.replace('SQLField','Field')
        data = data.replace('db.Field','Field')
        data = data.replace('accepts(request.vars','accepts(request')
        data = data.replace('URL(r=request,f=','URL(')
        data = data.replace('URL(r=request,f=','URL(')
        open(f,'w').write(data)

def find_similar_layouts():
    apps = glob.glob('*')
    keys = {}
    for app in apps:
        if os.path.isdir(app):
            try:
                data = open(app+'/views/layout.html').read()
                layout = hash(data[-20:]+data[:20])
                keys[layout]=keys.get(layout,[]) + [app]
            except:
                continue
            
    for key in keys: 
        if len(keys[key])>3:
            print keys[key]

def fix_layouts():
    apps = glob.glob('*')
    keys = {}
    for app in apps:
        if os.path.isdir(app):
            os.system('cp welcome/controllers/appadmin.py %s/controllers/' % app)
            os.system('cp welcome/views/default/user.html %s/views/default/' % app)
            os.system('cp welcome/views/appadmin.html %s/views/' % app)
            if app in ['cookbook', 'inno', 'radiologs', 'semaprinter', 'sqldesigner', 'sysadmin']+['cards', 'carstore', 'dna', 'doc_net', 'fbconnect', 'mazes', 'trains']+['ajaxspreadsheet', 'bingapi', 'filemanager', 'spreadsheet']+['email_form', 'geoip', 'imagegallery', 'isup', 'MetraSchedule', 'processingjs', 'pyforum2', 'videotest']:
                os.system('cp welcome/views/layout.html %s/views/' % app)
                os.system('cp -r welcome/static/ %s/static/' % app)
                os.system('cp welcome/views/web2py_ajax.html %s/views/' % app)

            elif os.path.exists('%s/static/js' % app):
                os.system('cp welcome/static/js/*.js %s/static/js' % app)

def allfiles(rootdir):
    fileList = []
    for root, subFolders, files in os.walk(rootdir):
        for file in files:
            fileList.append(os.path.join(root,file))
    return fileList

def unlinkedstatic(path):
    af = allfiles(path)
    for f in af:
        if f.split('/')[1]=='static' and \
                f.split('/')[2] in ('images','css','js'):
            name = f.split('/')[-1]
            linked = False
            for g in af:
                if not f==g and os.path.exists(g) and open(g,'r').read().find(name)>=0:
                    linked = True
                    break
            if not linked:
                os.unlink(f)

def unlinkedstaticall():
    apps = glob.glob('*')
    for app in apps:
        if os.path.isdir(app):
            unlinkedstatic(app)

def makeshots():
    "requires http://www.paulhammond.org/webkit2png/"
    apps = glob.glob('*')
    for app in apps:
        if os.path.isdir(app):
            os.system('webkit2png http://127.0.0.1:8000/%s' % app)
            os.system('mv 1270018000%s-full.png %s/shot-full.png' % (app,app))
            os.system('mv 1270018000%s-thumb.png %s/shot-thumb.png' % (app,app))
            os.system('rm 1270018000%s-clipped.png' % app)

def check_works():
    apps = glob.glob('*')
    for app in apps:
        if os.path.isdir(app):
            page = urllib.urlopen('http://127.0.0.1:8000/'+app).read()
            if 'Ticket' in page:
                print app,'issued a ticket'
                return False
    return True

def build_w2p():
    apps = glob.glob('*')
    for app in apps:
        if os.path.isdir(app):
            print file,'...',
            os.chdir(app)
            os.system('tar zcvf web2py.app.%s.w2p * > ../build.log' % app)
            os.chdir('..')

def rename():
    apps = glob.glob('*')
    for app in apps:
        if os.path.isdir(app):
            name = raw_input(app+' >>>')
            if name and name.lower()!=app.lower():
                os.system('mkdir %s' % name)
                os.system('mv %s/* %s' % (app,name))
                os.system('rmdir %s' % app)

def makeservice():
    apps = [app for app in glob.glob('*') if os.path.isdir(app)]
    open('apps.json','w').write(simplejson.dumps(apps))

if True:
    cleanup()    
    fixoldsyntax()
    unlinkedstaticall()
    fix_layouts()
    if check_works():
        makeshots()
        cleanup()    
        build_w2p()
makeservice()
