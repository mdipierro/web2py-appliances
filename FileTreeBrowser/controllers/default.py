# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    response.flash = T('Welcome to web2py')
    return dict(message=T('Hello World'))
    
    
"""
def thumnails():
  import glob
  import Image 
  folder=request.post_vars.folder
  application=request.application
  
  for infile in glob.glob(application+"/static/pictures/"+folder+"/*.jpg"):
    im = Image.open(infile)
    if infile[0:2] != "T_":
      im.thumbnail((128, 128), Image.ANTIALIAS)
      im.save("T_" + infile, "JPEG")
"""


def dirlist():
   import os
   import urllib
   import re 

   r=['<ul class="jqueryFileTree" style="display: none;">']
   try:
       r=['<ul class="jqueryFileTree" style="display: none;">']
       #To make absolute path to the server
       dir_server='/home/jose/web2py/applications/'
       #Add another path to our application
       application=request.application+'/static'
       dir_files=request.post_vars.dir
       #To prevent post code and try to see subdiretories
       expression='[.+~$]'
       regex = re.compile(expression) 
       if regex.match(dir_files):
	 r.append('Error con el tipo de carpeta. No debe contener caracteres raros.: %s' % str(dir_files))
	 return r
       d=urllib.unquote(dir_server+application+dir_files)
       regex = re.compile(expression) 
       for f in os.listdir(d):
           ff=os.path.join(d,f)
           if os.path.isdir(ff):
	       #To show the raltive path to the users and work with relative path on the size client
	       ff=os.path.join(dir_files,f)
               r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (ff,f))
           else:
	       #To show the raltive path to the users and work with relative path on the size client
	       ff=os.path.join(dir_files,f)
               e=os.path.splitext(f)[1][1:] # get .ext and remove dot
               r.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (e,ff,f))
       r.append('</ul>')
   except Exception,e:
       r.append('Could not load directory: %s' % str(dir_files))
   
   r.append('</ul>')
   return r


def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()


