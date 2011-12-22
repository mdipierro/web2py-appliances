# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

def index():
    return dict()

@auth.requires_login()
def list_music():
    return dict(table=plugin_jqgrid(db.music,columns=['id','name','file','date_onair'],col_widths={'id':50,'name':200,'file':150,'date_onair':100},width=400))

@auth.requires_login()
def edit_music():
    id=request.args(0)
    return dict(form=crud.update(db.music,id))

def do_this(form):
    import os
    name=IS_SLUG.urlify(form.vars.name)+'-'+str(form.vars.id)
    path=os.path.join(request.folder,'private',name)
    os.makedirs(path)

@auth.requires_login()
def list_programs():
    return dict(table=plugin_jqgrid(db.program,columns=['id','name'],col_widths={'id':100,'name':200},width=400),form=crud.create(db.program,onaccept=do_this))

@auth.requires_login()
def edit_program():
    id=request.args(0)
    return dict(form=crud.update(db.program,id))

@auth.requires_login()
def show_program():
    program_id=request.args(0)
    db.music.program.default=program_id
    db.music.program.writable=db.music.program.readable=False
    form=crud.create(db.music)
    table=plugin_jqgrid(db.music,'program',program_id,columns=['id','name','file','date_onair'],
                        col_widths={'id':50,'name':200,'file':150,'date_onair':100},width=400)
    return dict(table=table,form=form)

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
