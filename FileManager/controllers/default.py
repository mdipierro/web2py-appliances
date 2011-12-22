# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  
from __future__ import with_statement # This isn't required in Python 2.6     
__metaclass__ = type
import os
import sys
import time
try:
    from PIL import Image
except ImportError:
    raise HTTP(200,"Requires the Python Imaging Library installed")
from gluon.contrib import simplejson as json
import urllib
import datetime
now=datetime.datetime.now()
split_path = os.path.split
split_ext = os.path.splitext
path_exists = os.path.exists
normalize_path = os.path.normpath
absolute_path = os.path.abspath 
encode_urlpath = urllib.quote_plus
output=os.path.join(request.folder,'static','test.txt')



def index():
    appname=request.application
    return dict(appname=appname)
    
@service.json
def getinfo(path):
    if path=='True':
        path=request.vars.path
    else:
        path=path
    row=db((db.allfiles.filepath==path)&(db.allfiles.user==me)).select()[0]
    abspath=request.folder+path
    iconfolder='static/images/fileicons/'
    absiconlocation=request.folder+iconfolder
    iconlocation='/'+request.application+'/'+iconfolder
    filename=row.filename
    filetype=row.filetype
    datecreated=row.datecreated
    datemodified=row.datemodified
    filesize=row.filesize
    thefile = {
            'Filename' : filename,
            'FileType' : '',
            'Preview' : iconlocation+'_Open.png' if filetype=='dir' else '' ,
            'FilePreview':'',
            'Path' : path,
            'Error' : '',
            'Code' : 0,
            'Properties' : {
                    'Date Created' : '',
                    'Date Modified' : '',
                    'Width' : '',
                    'Height' : '',
                    'Size' : ''
             }
            }
            
    imagetypes = set(['gif','jpg','jpeg','png','bmp'])      
        
    if filetype=='dir':
        thefile['FileType'] = 'Directory'
    else:
        thefile['FileType'] = filetype  
        if filetype in imagetypes:
            thefile['Preview']='/'+request.application+'/default/download/'+row.file
        elif filetype=="mp3" or filetype=="flv":
            thefile['FileType']='media'
            embedfile='/'+request.application+'/default/download/'+row.file          
            thefile['FilePreview']=str(plugin_mediaplayer(embedfile,400,300))
            previewPath = iconlocation + filetype.lower() + '.png'
            abspreviewPath=absiconlocation+filetype.lower()+'.png'
            thefile['Preview'] = previewPath if os.path.exists(abspreviewPath) else iconlocation+'default.png'
        else:
            previewPath = iconlocation + filetype.lower() + '.png'
            abspreviewPath=absiconlocation+filetype.lower()+'.png'
            thefile['Preview'] = previewPath if os.path.exists(abspreviewPath) else iconlocation+'default.png'
        
    thefile['Properties']['Date Created'] = datecreated 
    thefile['Properties']['Date Modified'] = datemodified
    thefile['Properties']['Size'] = filesize
    return thefile
     
@service.json   
def getdata():
    path=request.vars.path
    data=db((db.allfiles.filepath==path)&(db.allfiles.user==me)).select()[0]
    textdata=data.content
    return textdata

def updatedata():
    data=request.vars.senddata
    path=request.vars.getpath
    db((db.allfiles.filepath==path)&(db.allfiles.user==me)).update(content=data)
    return 'Updated!!!'
 
@service.json
def getfolder():   
    path=request.vars.path
    rows=db((db.allfiles.parentpath==path)&(db.allfiles.user==me)).select()    
    result = {}
    for row in rows:
        result[row.filepath]=getinfo(row.filepath)
    return result

def browsefiles():
    files=db((db.allfiles.user==me)&(db.allfiles.filetype !='dir')).select()
    result={}
    filetypes= set(['gif','jpg','png','bmp','swf'])
    for rfile in files:
        if rfile.filepath[-3:] in filetypes:
            result[rfile.filepath]=getfileinfo(rfile.filepath)
    return dict(result=result,cknum=request.vars.CKEditorFuncNum)
    
def getfileinfo(path):
    row=db((db.allfiles.filepath==path)&(db.allfiles.user==me)).select()[0]
    abspath=request.folder+path
    iconfolder='static/images/fileicons/'
    absiconlocation=request.folder+iconfolder
    iconlocation='/'+request.application+'/'+iconfolder
    filename=row.filename
    filetype=row.filetype
    filesize=row.filesize
    thefile = {
            'Filename' : filename,
            'FileType' : '',
            'Preview' : iconlocation+'_Open.png' if filetype=='dir' else '' ,
            'FilePreview':'',
            'Path' : path,
            'Error' : '',
            'Code' : 0,
            'Properties' : {
                    'Width' : '',
                    'Height' : '',
                    'Size' : ''
             }
            }
            
    imagetypes = set(['gif','jpg','jpeg','png','bmp'])      
        
    if filetype=='dir':
        thefile['FileType'] = 'Directory'
    else:
        thefile['FileType'] = filetype  
        if filetype in imagetypes:
            thefile['Preview']='/'+request.application+'/default/download/'+row.file
        elif filetype=="mp3" or filetype=="flv":
            thefile['FileType']='media'
            embedfile='/'+request.application+'/default/download/'+row.file          
            thefile['FilePreview']=str(plugin_mediaplayer(embedfile,400,300))
            previewPath = iconlocation + filetype.lower() + '.png'
            abspreviewPath=absiconlocation+filetype.lower()+'.png'
            thefile['Preview'] = previewPath if os.path.exists(abspreviewPath) else iconlocation+'default.png'
        else:
            previewPath = iconlocation + filetype.lower() + '.png'
            abspreviewPath=absiconlocation+filetype.lower()+'.png'
            thefile['Preview'] = previewPath if os.path.exists(abspreviewPath) else iconlocation+'default.png'        
    thefile['Properties']['Size'] = filesize
    return thefile


def dirlist():
   import re
   r=['<ul class="jqueryFileTree" style="display: none;">']
   path=request.post_vars.dir
   rows=db((db.allfiles.parentpath==path)&(db.allfiles.user==me)).select()
   if len(rows)==0 and path=='/':
        Directories=['Documents','Audios','Videos','Pictures','Other']
        parentpath='/'
        for directory in Directories:
            filename=directory
            filepath='/'+filename+'/'
            db.allfiles.insert(filename=filename,filepath=filepath,parentpath=parentpath,filetype='dir',datecreated=now,user=me)
   rows=db((db.allfiles.parentpath==path)&(db.allfiles.user==me)).select()
   for row in rows:
       if row.filetype=='dir':
          r.append('<li class="directory collapsed"><a href="#" rel="%s">%s</a></li>' % (row.filepath,row.filename))    
   r.append('</ul>')
   return r

@service.json
def addfolder(param):    
    filename=request.vars.name.replace(' ','_')
    parentpath=request.vars.path
    filepath=parentpath+filename+'/'
    rows=db((db.allfiles.filepath==filepath)&(db.allfiles.user==me)).select()
    recordexists=len(rows)
    if not recordexists:
        db.allfiles.insert(filename=filename,filepath=filepath,parentpath=parentpath,filetype='dir',datecreated=now,user=me)
        result= {
                    'Parent' : parentpath,
                    'Name' : filename,
                    'Error' :'',
                    'Code' :0
                    }
    else:
        result = {
                    'Path' : parentpath,
                    'Name' : filename,
                    'Code' : 1,
                    'Error' : 'Folder already exists'
                }
    return result
    
@service.json
def delete(param):
    path=request.vars.path
    #print "<--------------delete---------->"
    #print "path:",path
    filepaths=remove(path,pathset=[])
    for filepath in filepaths:
        if not filepath[-1]=='/':
            row=db((db.allfiles.filepath==filepath )&(db.allfiles.user==me)).select()[0]
            filename=row.file
            os.remove(os.path.join(request.folder,'uploads',filename))
        db((db.allfiles.filepath==filepath )&(db.allfiles.user==me)).delete()    
    result={
            'Error':'No Error',
            'Code':0,
            'Path': path 
           }        
    return result
     
@service.json
def rename(param):
    #print "<---------rename--------->"
    oldpath=request.vars.old  
    #print "oldpath:",oldpath      
    #print "parentpath:",parentpath
    newname = request.vars.new.replace(' ','_')    
    result={
            'type':'',
            'Old Path':'',
            'New Path':'',
            'Old Name':'',
            'New eName':'',
            'parent':'',
            'Code':0,
            'Error':''
            } 
    if oldpath[-1]=='/':
        oldname=split_path(oldpath[:-1])[-1]
        parentpath=split_path(oldpath[:-1])[0]
        if not parentpath=='/':
            parentpath=parentpath+'/'
        row=db((db.allfiles.parentpath==parentpath)&(db.allfiles.filetype=='dir') \
        &(db.allfiles.filename==newname)&(db.allfiles.user==me)).select()
        if len(row)==1:
            result['Code']=1
            result['Error']='Folder already exists'
            return result
        newpath=parentpath+newname+'/'
        result['type']='dir'
        db((db.allfiles.filepath==oldpath)&(db.allfiles.user==me)).update(filepath=newpath,filename=newname,datemodified=now)
        renamedir(oldpath,oldname,newname)
    else:   
        oldname = split_path(oldpath)[-1]
        parentpath = split_path(oldpath)[0]
        if not parentpath=='/':
            parentpath=parentpath+'/'        
        newpath = parentpath + newname
        row=db((db.allfiles.parentpath==parentpath)&(db.allfiles.filepath==newpath)&(db.allfiles.user==me)).select()
        if len(row)==1:
            result['Code']=1
            result['Error']='File already exists'
            return result
        result['type']='file'
        db((db.allfiles.filepath==oldpath)&(db.allfiles.user==me)).update(filepath=newpath,filename=newname,datemodified=now)
    result['parent']=parentpath
    result['Old Path']= oldpath
    result['Old Name']=oldname
    result['New Path']=newpath
    result['New eName']=newname    
    return result 
    
def renamedir(oldpath,oldname,newname):
    newpath=oldpath.replace(oldname,newname)
    rows=db((db.allfiles.parentpath==oldpath)&(db.allfiles.user==me)).select()
    for row in rows:
        if row.filepath[-1]=='/':
            db((db.allfiles.parentpath==oldpath) \
            &(db.allfiles.user==me)).update(parentpath=row.parentpath.replace(oldname,newname),datemodified=now)
            renamedir(row.filepath,oldname,newname)
            db((db.allfiles.filepath==row.filepath) \
            &(db.allfiles.user==me)).update(filepath=row.filepath.replace(oldname,newname),datemodified=now)
        else:
            db((db.allfiles.filepath==row.filepath)&(db.allfiles.user==me)). \
            update(filepath=row.filepath.replace(oldname,newname),parentpath=row.parentpath.replace(oldname,newname),datemodified=now)
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


def add():   
    parentpath=request.vars.currentpath
    file=request.vars.file
    filename=file.filename.replace(' ','_')
    
    filepath=parentpath+filename
    filetype=os.path.splitext(filename)[1][1:]
    row=db((db.allfiles.parentpath==parentpath)&(db.allfiles.filepath==filepath)&(db.allfiles.filename==filename) \
    &(db.allfiles.user==me)).select()
    if not len(row):    
        db.allfiles.insert(filename=filename,filepath=filepath, \
            parentpath=parentpath,filetype=filetype,file=db.allfiles.file.store(file.file,filename),datecreated=now,user=me)   
        result = {
                'Path' : parentpath,
                'Name' : filename,
                'Error' :'',
                'Code':0
            }
    else:
        result = {
                'Path' : parentpath,
                'Name' : filename,
                'Error' : 'File already exists',
                'Code':1
            }
        return '<textarea>'+str(result)+'</textarea>'
    row=db((db.allfiles.filename==filename)&(db.allfiles.user==me)).select()[0]
    insertedfile=row.file
    outfile=open(output,'wb')
    try:
        filepath=os.path.join(request.folder,'uploads',insertedfile)
        filesize=os.path.getsize(filepath)
        if filepath[-3:]=='txt' or filepath[-4:]=='html':
            filepath=os.path.normpath(filepath)
            filein=open(filepath,'r')
            dbcontent=filein.read()
            filein.close()
            db((db.allfiles.filename==filename)&(db.allfiles.user==me)).update(filesize=filesize,content=dbcontent)
        else:
            db((db.allfiles.filename==filename)&(db.allfiles.user==me)).update(filesize=filesize)
        outfile.close()        
    except:
        outfile.write(str(sys.exc_info()[1]))
        outfile.close()   
    return '<textarea>'+str(result)+'</textarea>'

def downloadurl():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    filename=request.vars.filename
    file=db((db.allfiles.filename==filename)&(db.allfiles.user==me)).select()[0]   
    return file.file

def download():
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


def remove(path,pathset):
    if path[-1]=='/':
        pathset.append(path)
        rows=db((db.allfiles.parentpath==path)&(db.allfiles.user==me)).select()
        for row in rows:
            if row.filetype=='dir':
                remove(row.filepath,pathset=pathset)
            else:
                pathset.append(row.filepath)
    else:
        pathset.append(path)
    return pathset
