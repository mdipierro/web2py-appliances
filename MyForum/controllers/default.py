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

def index():
    if_author = lambda row: (row.created_by==auth.user_id or auth.has_membeship('moderators'))
    db.forum.name.represent = lambda name,row: A(name,_href=URL('forum',args=(row.id,IS_SLUG.urlify(name))))
    grid = SQLFORM.grid(db.forum,orderby=~db.forum.views,editable=if_author,deletable=if_author,
                        details=False,create=False,csv=False)
    return locals()

@auth.requires_login()
def create_forum():
    db.forum.views.readable = db.forum.last_updated.readable = False
    form = SQLFORM(db.forum,formstyle='table2cols').process(next='forum/[id]')
    return locals()

def forum():
    if request.post_vars.parent_id=='0': request.post_vars.parent_id=None
    forum = db.forum(request.args(0,cast=int)) or redirect(URL('index'))
    if not forum.id in session.forums:
        session.forums.append(forum.id)
        forum.update_record(views=forum.views+1)
    db.post.forum.default=forum.id    
    form = SQLFORM(db.post) if auth.user else None
    if form:
        form.process()
        if form.accepted:
            forum.update_record(last_updated = request.now)
        elif form.errors:
            form.errors.clear() # do not post an empty post, just ignore it
    posts = db(db.post.forum==forum.id).select(orderby=db.post.created_on).as_trees()
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
def get_posts(id):
    return db(db.post.forum==id).select(orderby=db.post.created_on).as_json()

@auth.requires_login()
def call():
    return service()

