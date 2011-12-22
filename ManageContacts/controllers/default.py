# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    return dict()

def companies():
    companies = db(db.company).select(orderby=db.company.name)
    return locals()

def contacts():
    company = db.company(request.args(0)) or redirect(URL('companies'))
    contacts = db(db.contact.company==company.id).select(orderby=db.contact.name)
    return locals()

@auth.requires_login()
def company_create():
    form = crud.create(db.company,next='companies')
    return locals()

@auth.requires_login()
def company_edit():
    company = db.company(request.args(0)) or redirect(URL('companies'))
    form = crud.update(db.company,company,next='companies')
    return locals()

@auth.requires_login()
def contact_create():
    db.contact.company.default=request.args(0)
    form = crud.create(db.contact,next='companies')
    return locals()

@auth.requires_login()
def contact_edit():
    contact = db.contact(request.args(0)) or redirect(URL('companies'))
    form = crud.update(db.contact,contact,next='companies')
    return locals()

@auth.requires_login()
def contact_logs():
    contact = db.contact(request.args(0)) or redirect(URL('companies'))
    logs = db(db.log.contact==contact.id).select(orderby=db.log.posted_on)
    db.log.contact.default = contact.id
    db.log.contact.readbale = False
    db.log.contact.writable = False
    db.log.posted_on.default = request.now
    db.log.posted_on.readable = False
    db.log.posted_on.writable = False
    form = crud.create(db.log)
    return locals()

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
