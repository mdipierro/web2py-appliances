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
    lists = db(db.restaurant.is_special==True ).select(orderby=db.restaurant.name)
    return dict(lists=lists)

def show():
    store = db(db.restaurant.id==request.args(0)).select()
    return dict(store=store)

@auth.requires_login()
def favorite():
    query = (db.favorite.user==auth.user.id) & (db.favorite.restaurant_id == db.restaurant.id) 
    lists = db(query).select(db.restaurant.ALL)
    return dict(lists=lists)
    
def update_favorite():
    if request.args(0)=='add':
        db.favorite.insert(user=request.args(1),restaurant_id=request.args(2))
        session.flash = "Added to your favorites"
        redirect(URL('favorite'))
    elif request.args(0)=='remove':
        db((db.favorite.user==request.args(1)) & (db.favorite.restaurant_id==request.args(2))).delete()
        session.flash = "Removed from your favorites"
        redirect(URL('favorite'))
    return dict()

@auth.requires_membership('owner')
def update():
    myrestaurant = db.restaurant(db.restaurant.owner_id==auth.user.id)
    db.special.restaurant_id.default = myrestaurant.id
    db.special.restaurant_id.writable = False
    grid = SQLFORM.grid(db.special.restaurant_id==request.args(0),fields=[db.special.id,db.special.name,db.special.price],paginate=10,details=False,csv=False,searchable=False)
    return dict(grid=grid,) 

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
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
