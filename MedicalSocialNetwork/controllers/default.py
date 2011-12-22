# -*- coding: utf-8 -*-

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    if not auth.user: redirect(URL('user'))
    return dict()

@auth.requires_login()
def patient_info():
    patient=db.auth_user[request.args(0)]
    return dict(patient=patient)

@auth.requires_login()
def patient():
    patient=db.auth_user[request.args(0)] or redirect(URL('search'))
    trusted_by(patient)
    table=request.args(1)
    if not table in ['contact','insurance']: redirect(URL('search'))
    record=db[table][request.args(2)]
    if not record or record.patient==patient.id:
        db[table].patient.default=patient.id
        form=crud.update(db[table],record)
    else:
        form=None
    rows = plugin_wiki.widget('jqgrid',table,'patient',patient.id)
    return dict(form=form,rows=rows)

@auth.requires_login()
def patient_insurance():
    return dict()

@auth.requires_login()
def backlog():
    patient=db.auth_user[request.args(0)]
    if not patient or not patient.patient:
        session.flash='Not authorized: not a patient'
        redirect(URL('index'))
    elif patient.id==auth.user.id:
        form=None
    elif trusted_by(patient):
        db.post.patient.default=patient.id
        db.post.reasons.requires=IS_IN_DB(db(db.post.patient==patient.id),'post.id','%(posted_on)s %(title)s',multiple=True)
        form = crud.create(db.post,next=URL(r=request,args=request.args))
    posts = db(db.post.patient==patient.id).select(orderby=~db.post.posted_on)
    return dict(form=form,posts=posts,patient=patient)

@auth.requires_login()
def post_edit():
    post=db.post[request.args(0)]
    if not post.posted_by==auth.user.id:
        session.flash='Not authorized'
        redirect(URL('index'))
    db.post.reasons.requires=IS_IN_DB(db(db.post.patient==post.patient),'post.id','%(posted_on)s %(title)s',multiple=True)
    db.post.expired.writable=db.post.expired.readable=True
    db.post.expires_on.writable=db.post.expires_on.readable=True
    form = crud.update(db.post,post,next=URL('backlog',args=post.patient))
    return dict(form=form)

@auth.requires(auth.user and (auth.user.nurse or auth.user.doctor or auth.user.administrator))
def new_patient():
    return dict(form=crud.create(db.auth_user))

@auth.requires(auth.user and (auth.user.nurse or auth.user.doctor or auth.user.administrator))
def search():
    return dict(grid=PluginWikiWidgets.jqgrid(db.auth_user,'patient',True,fields='id,first_name,last_name,sex,birth_date'))


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


