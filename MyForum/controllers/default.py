# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

print request.env.path_info, request.post_vars

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

session.forums = session.forums or []
session.threads = session.threads or []

def index():
    response.menu.append(('New Forum',False,URL('create_forum')))
    if_author = lambda row: (row.created_by==auth.user_id or auth.has_membeship('moderators'))
    db.forum.name.represent = lambda name,row: A(name,_href=URL('forum',args=(row.id,IS_SLUG.urlify(name))))
    grid = SQLFORM.grid(db.forum,orderby=~db.forum.views|~db.forum.created_on,
                        editable=if_author,deletable=if_author,
                        details=False,create=False,csv=False)
    return locals()

@auth.requires_login()
def create_forum():
    db.forum.views.readable = db.forum.last_updated.readable = False
    form = SQLFORM(db.forum,formstyle='table2cols').process(next='forum/[id]')
    return locals()

def forum():
    forum = db.forum(request.args(0,cast=int)) or redirect(URL('index'))
    response.menu.append(('New Thread',False,URL('create_thread',args=forum.id)))
    if_author = lambda row: (row.created_by==auth.user_id or auth.has_membeship('moderators'))
    db.thread.name.represent = lambda name,row: A(name,_href=URL('thread',args=(row.id,IS_SLUG.urlify(name))))
    grid = SQLFORM.grid(db.thread.forum==forum.id,orderby=~db.thread.views|~db.thread.created_on,
                        editable=if_author,deletable=if_author,args=request.args[:2],
                        details=False,create=False,csv=False)
    return locals()

@auth.requires_login()
def create_thread():
    forum = db.forum(request.args(0,cast=int)) or redirect(URL('index'))
    db.thread.views.readable = db.thread.last_updated.readable = False
    form = SQLFORM.factory(Field('name',requires=NE),
                           Field('body','text',requires=NE),formstyle='table2cols').process()
    if form.accepted:
        tid = db.thread.insert(name=form.vars.name,forum=forum.id)
        db.post.insert(thread=tid,body=form.vars.body)
        redirect(URL('thread',args=tid))
    return locals()

def thread():
    thread = db.thread(request.args(0,cast=int)) or redirect(URL('index'))
    forum = db.forum(thread.forum) or redirect(URL('index'))
    print forum
    response.menu.append(('This Forum',False,URL('forum',args=forum.id)))
    if not forum in session.forums:
        session.forums.append(forum)
        forum.update_record(views=forum.views+1)
    if not thread.id in session.threads:
        session.threads.append(thread.id)
        thread.update_record(views=thread.views+1)
    if request.post_vars.parent_id in ('0',None):
        request.post_vars.parent_id=None
    else:
        parent_post = db.post(request.post_vars.parent_id)
        db.post.nesting_level.default = parent_post.nesting_level+1
    db.post.thread.default = thread.id    
    form = SQLFORM(db.post) if auth.user else None
    if form:
        form.process()
        if form.accepted:
            thread.update_record(last_updated = request.now)
            forum.update_record(last_updated = request.now)
        elif form.errors:
            form.errors.clear() # do not post an empty post, just ignore it
    posts = db(db.post.thread==thread.id).select(orderby=db.post.created_on).as_trees()
    return locals()

@auth.requires_login()
def do():
    id, method = request.args(0,cast=int), request.args(1)
    if method == 'report':
        db(db.post.id==id).update(reported=True)
        return 'reported'
    if method == 'approve' and (DEBUG or auth.has_membership('moderators')):
        db(db.post.id==id).update(reported=False, approved=True,banned=False)
        return 'approved'
    if method == 'banned' and (DEBUG or auth.has_membership('moderators')):
        db(db.post.id==id).update(banned=True,approved=False,reported=False)
        return 'banned'
    if method == 'delete':
        db(db.post.id==id)(db.post.created_by==auth.user_id).update(deleted=True)
        return 'deleted'    
    return ''

def user():
    return dict(form=auth())

@cache.action()
def download():
    return response.download(request, db)

@service.json
def get_forums():
    return db(db.forum).select(orderby=db.forum.created_on).as_json()

@service.json
def get_threads(forum_id):
    return db(db.thread.forum==forum_id).select(orderby=db.thread.created_on).as_json()

@service.json
def get_posts(thread_id):
    return db(db.post.thread==thread_id).select(orderby=db.post.created_on).as_json()

@auth.requires_login()
def call():
    return service()

