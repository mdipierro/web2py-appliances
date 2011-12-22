import cgi

@auth.requires_login()
def index():
    chats=accessible('chat_line',('read','read/chat'))(db.chat_line.owner==db.auth_user.id).select(orderby=db.chat_line.name,groupby=db.chat_line.id)
    return dict(chats=find_groups(chats))

@auth.requires_login()
def create_chat():
    form=SQLFORM(db.chat_line,fields=db.chat_line.public_fields)
    form.vars.owner=auth.user_id
    if form.accepts(request,session):
        id=db.access.insert(persons_group=g_tuple[1],table_name='chat_line',\
                            record_id=form.vars.id,access_type='read/chat')
        session.flash='chat line created'
        redirect_change_permissions(db.chat_line,form.vars.id)
    return dict(form=form)

@auth.requires_login()
def edit_chat():
    if len(request.args)<1: redirect(URL('index'))
    rows=db(db.chat_line.id==request.args[0])\
           (db.chat_line.owner==auth.user_id).select()
    if not len(rows): redirect(URL('index'))
    form=SQLFORM(db.chat_line,rows[0],deletable=True,\
                 fields=db.chat_line.public_fields,showid=False)
    if form.accepts(request,session):
        if request.vars.delete_this_record=='on':
            session.flash='chat line deleted for good'
        else:
            session.flash='chat line info saved'
        redirect(URL('index'))
    return dict(form=form)

@auth.requires_login()
def open_chat():
    if len(request.args)<1: redirect(URL('index'))
    chat_id=request.args[0]
    access=has_access(auth.user_id,'chat_line',chat_id,('read','read/chat'))
    if not access:
        session.flash='access denied'
        redirect(URL('index'))
    chat_line=db(db.chat_line.id==chat_id).select()[0]
    readonly=access.access_type=='read'
    return dict(readonly=readonly,chat_line=chat_line)

@auth.requires_login()
def clear():
    chat_id=request.args[0]
    if len(db(db.chat_line.id==chat_id)(db.chat_line.owner==auth.user_id).select()):
        db(db.message.chat_line==chat_id).delete()
    redirect(URL('index'))

@auth.requires_login()
def post():
    chat_id=request.args[0]
    access=has_access(auth.user_id,'chat_line',chat_id,('read','read/chat'))
    if not access: raise HTTP(400)
    if request.vars.message and access.access_type=='read/chat':
        db.message.insert(body=request.vars.message.strip(),\
                          posted_by=auth.user_id,chat_line=chat_id)
    messages=db(db.message.chat_line==chat_id)\
        (db.message.posted_by==db.auth_user.id)\
        (db.message.id>(request.post_vars.last or 0))\
        .select(orderby=db.message.posted_on)
    posts=[[m.message.id,str(m.message.posted_on),\
            cgi.escape(m.auth_user.name),m.auth_user.email,
            cgi.escape(m.message.body).replace('//','<br/>')] \
           for m in messages]
    import gluon.contrib.simplejson as sj
    return sj.dumps(posts)


def rss():
    response.headers['Content-Type']='application/rss+xml'
    import gluon.contrib.rss2 as rss2
    requested_groups=request.vars.groups or '1'
    try: requested_groups=tuple([int(i) for i in requested_groups.split(',')])
    except: return ''
    entries=db(db.announcement.id==db.access.record_id)\
            (db.access.table_name=='announcement')\
            (db.access.auth_users_group.belongs(requested_groups))\
            (db.announcement.to_rss==True)\
            (db.auth_user.id==db.announcement.owner)\
            .select(groupby=db.announcement.id)
    items = [rss2.RSSItem(
               title=entry.announcement.title,
               link=MAIN,
               author=entry.auth_user.email,
               description = entry.announcement.body,
               pubDate = entry.announcement.posted_on) for entry in entries]
    rss = rss2.RSS2(title='public rss for '+str(requested_groups),
       link = MAIN,
       description = str(requested_groups),
       lastBuildDate = datetime.datetime.now(),
       items=items)
    return rss2.dumps(rss)

