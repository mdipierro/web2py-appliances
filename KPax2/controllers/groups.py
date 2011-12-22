@auth.requires_login()
def index():
    form=FORM(INPUT(_name='group',requires=IS_MATCH('(g|G)\d+')),
              INPUT(_type='submit',_value='join!'))
    if form.accepts(request,formname='join_group'):
        persons_group=int(form.vars.group[1:])
        groups=db(db.persons_group.id==persons_group).select()
        if persons_group in g_tuple:
            response.flash='you are already a member of the group'
        elif len(groups)==0:
            response.flash='unkown group'
        elif has_access(auth.user_id,'persons_group',persons_group,'see/join') or \
                groups[0].open==True:
            db.membership.insert(person=auth.user_id,persons_group=persons_group)
            session.groups=get_groups(auth.user_id)
            g_tuple[:]=[g.id for g in session.groups]
            response.flash='group joined'
        else:
            db.membership_request.insert(person=auth.user_id,persons_group=persons_group)
            session.groups=get_groups(auth.user_id)
            g_tuple[:]=[g.id for g in session.groups]
            response.flash='your request to join was submitted'
    mygroups=db(db.persons_group.id.belongs(g_tuple))\
               (db.persons_group.owner==db.auth_user.id).select(orderby=db.persons_group.name.upper())
    return dict(mygroups=mygroups,form=form)

@auth.requires_login()
def unjoin():
    if len(request.args) and \
       not int(request.args[0]) in [g_tuple[0],g_tuple[1]]:
        db(db.membership.persons_group==request.args[0]).delete()
    redirect(URL('index'))

@auth.requires_login()
def members():
    members=db(db.membership.persons_group==request.args[0])\
              (db.membership.person==db.auth_user.id).select()
    return dict(members=members)

@auth.requires_login()
def approve():
    if len(request.args) and len(db(db.persons_group.id==request.args[0])(db.persons_group.owner==auth.user_id).select()):
       for item in request.vars.items():
           if item[1]=='approve':
                req=db(db.membership_request.id==item[0]).select()[0]
                db(db.membership_request.id==item[0]).delete()
                db.membership.insert(persons_group=req.persons_group,person=req.person)
           elif item[1]=='deny':
                db(db.membership_request.id==item[0]).delete()
    pending=db(db.membership_request.persons_group==request.args[0])\
              (db.membership_request.person==db.auth_user.id).select()
    if len(pending)==0:
        session.flash='no pending applications for membership'
        redirect(URL('index'))
    return dict(pending=pending)

@auth.requires_login()
def create_group():
    form=SQLFORM(db.persons_group,fields=db.persons_group.public_fields)
    form.vars.owner=auth.user_id
    if form.accepts(request,session):
        db.membership.insert(person=auth.user_id,persons_group=form.vars.id)
        session.flash='group created'
        redirect_change_permissions(db.persons_group,form.vars.id)
    return dict(form=form)

@auth.requires_login()
def edit_group():
    if len(request.args)<1: redirect(URL('index'))
    rows=db(db.persons_group.id==request.args[0])\
           (db.persons_group.owner==auth.user_id).select()
    if not len(rows): redirect(URL('index'))
    form=SQLFORM(db.persons_group,rows[0],fields=db.persons_group.public_fields,
                 deletable=True)
    if form.accepts(request,session):
        if request.vars.delete_this_record=='on':
            session.flash='group deleted'
        else:
            session.flash='group saved'
        redirect(URL('index'))
    return dict(form=form)
