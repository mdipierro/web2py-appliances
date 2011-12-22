# -*- coding: utf-8 -*-

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

@auth.requires_login()
def newmovie():
    return dict(form=crud.create(db.movie),
                 movies=db(db.movie.id>0).select())

@auth.requires_login()
def category():
    return dict(form2=crud.create(db.category),
                 category=db(db.category.id>0).select())

@auth.requires_login()
def country():
    return dict(form3=crud.create(db.country),
                 country=db(db.country.id>0).select())

@auth.requires_login()
def format():
    return dict(form4=crud.create(db.format),
                 format=db(db.format.id>0).select())

def start():
    return dict (string="Start",)

def rules():
    return dict (string="Rules and Regulations",)

@auth.requires_login()
def movies():
    if not request.vars.movienum:
        movienum=0
    else:
        movienum=int(request.vars.movienum)
        session.movienum=request.vars.movienum
    return dict (string="Movies",
        movies=db(db.movie.id>0).select(orderby=db.movie.name, limitby=(movienum,movienum+20)),movienum=movienum)

@auth.requires_login()
def userlist():
    return dict (string="Users",)

@auth.requires_login()
def movie_by_user():
     rows=db(db.movie.id.belongs(db(db.review.author==request.args(0)).select(db.review.movie))).select()
     return dict(rows=rows)

@auth.requires_login()
def moviereview():
    rows=db(db.movie.id.belongs(db(db.review.author==request.args(0)).select(db.review.movie))).select()
    return dict (string="Movie Reviews",)


def userlogin():
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

@auth.requires_login()
def index():
    return dict(form=crud.create(db.movie),
                 movies=db(db.movie.id>0).select())


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
