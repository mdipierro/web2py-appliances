# -*- coding: utf-8 -*-

def index():
    magazine = db.magazine(request.args(0))
    if request.vars.keywords:
        def search(title):
            title=title.lower()
            return reduce(lambda a,b:a&b,[k in title for k in request.vars.keywords.lower().split()])
        articles = db(db.article.magazine==3026).select().find(lambda r: search(r.title)).sort(lambda r:r.sortable)
        magazine = None
    elif magazine:
        articles = db(db.article.magazine==magazine.id).select().sort(lambda r:r.sortable)
        response.meta.description = "CiSE, IEEE, AIP, " + magazine.title
    else:
        articles = None
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

@request.restful()
def auto():
    def GET(*args,**vars):
        parsed = db.parse_as_rest('auto',args,vars)
        if parsed.status==200: return dict(content=parsed.response)
        raise HTTP(parsed.status,parsed.error)
    return locals()
