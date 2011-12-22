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
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    return dict(message=T('Hello World'))

def search():
    classification = request.args(0) or redirect(URL('index'))
    form = SQLFORM.factory(Field('search',default=request.get_vars.search),
                           _method='GET')
    import urllib
    from gluon.contrib.feedparser import parse
    URL = 'http://export.arxiv.org/api/query?search_query=%s'
    if form.accepts(request.get_vars):
        query = urllib.quote(' AND '.join(['cat:'+classification]+\
                ['all:'+k for k in form.vars.search.strip().split()]))
        entries = parse(URL % query)['entries'] # title, 
    else:
        entries = []
    return dict(form=form,entries=entries)

def paper():
    id_list = request.vars.id_list or redirect(URL('index'))
    paper = db.paper(id_list==id_list) 
    if not paper:
        #import urllib
        #from gluon.contrib.feedparser import parse
        #URL = 'http://export.arxiv.org/api/query?id_list='+id_list
        #entry = parse(URL)
        paper_id = db.paper.insert(id_list=id_list)
    else:
        paper_id = paper_id
    title = request.vars.title or redirect(URL('index'))
    updated = request.vars.updated or redirect(URL('index'))
    author = request.vars.author or redirect(URL('index'))
    pdf = request.vars.pdf or redirect(URL('index'))
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
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id[
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def demo():
    return locals()
