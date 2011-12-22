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

def categories():
    categories = db(db.category).select(orderby=db.category.name)
    return locals()

def news():
    category = db.category(request.args(0)) or redirect(URL('categories'))
    news = db(db.news.category==category.id).select(orderby=~db.news.votes,limitby=(0,25))
    return locals()

@auth.requires_membership('manager')
def category_create():
    form = crud.create(db.category,next='categories')
    return locals()

@auth.requires_membership('manager')
def category_edit():
    category = db.category(request.args(0)) or redirect(URL('categories'))
    form = crud.update(db.category,category,next='categories')
    return locals()

@auth.requires_login()
def news_create():
    db.news.category.default = request.args(0)
    db.news.votes.default = 0
    form = crud.create(db.news,next='news_comments/[id]')
    return locals()

@auth.requires_login()
def news_edit():
    news = db.news(request.args(0)) or redirect(URL('categories'))
    if not news.posted_by==auth.user.id: redirect(URL('not_authorized'))
    form = crud.update(db.news,category,next='news_comments/[id]')
    return locals()

def news_comments():
    news = db.news(request.args(0)) or redirect(URL('categories'))
    if auth.user:
        db.comment.parent_comment.default = request.args(1)
        db.comment.news.default = news.id
        db.comment.posted_on.default = request.now
        db.comment.posted_by.default = auth.user.id
        form = crud.create(db.comment)
    comments = db(db.comment.news==news.id).select(orderby=db.comment.posted_on)
    return locals()

@auth.requires_login()
def vote():
    if request.env.request_method!='POST': raise HTTP(400) 
    news_id, mode = request.args(0), request.args(1)
    news = db.news(id=news_id)
    vote = db.vote(posted_by=auth.user.id,news=news_id)
    votes = news.votes
    value = (mode=='plus') and +1 or -1
    if vote and value*vote.value==1:
        message = 'you voted already'
    else:
        if vote:
            votes += value - vote.value
            vote.update_record(value=value)
        else:
            votes += value
            db.vote.insert(value=value,posted_by=auth.user.id,posted_on=request.now,news=news_id)
        news.update_record(votes=votes)
        message = 'vote recorded'
    return "$('#votes').html('%s');$('.flash').html('%s').slideDown();" % (votes,message)
    

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
