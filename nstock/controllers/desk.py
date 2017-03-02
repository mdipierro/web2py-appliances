# -*- coding: utf-8 -*-
if False:
    from gluon import current, URL, SQLFORM, redirect
    from gluon import IS_NOT_EMPTY, Field
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T
    from db import db, auth
    from dc import application


@auth.requires(
    lambda: auth.has_permission('owner', db.desk, request.args(0)) or
    (auth.has_permission('read', db.desk, request.args(0)) or
     auth.has_permission('update', db.desk, request.args(0)) or
     auth.has_permission('update_items', db.desk, request.args(0)))
)
def index():
    """Show the list of items in this desk"""
    desk = db.desk(request.args(0))

    if desk.id == application.getUserDesk().id:
        session.org_id = None
    session.desk_id = desk.id
    # used to mark items for package creation
    session.marked_items = []

    return locals()


@auth.requires(
    lambda: auth.has_permission('owner', db.desk, request.args(0)) or
    (auth.has_permission('read', db.desk, request.args(0)) or
     auth.has_permission('update', db.desk, request.args(0)) or
     auth.has_permission('update_items', db.desk, request.args(0)))
)
def item_list():
    """Show the list of items in this desk"""
    desk = db.desk(request.args(0))

    if desk.id == application.getUserDesk().id:
        session.org_id = None
    session.desk_id = desk.id

    return locals()


@auth.requires_login()
def toogle_mark():
    if session.marked_items is None:
        session.marked_items = []

    item = application.getItemByUUID(request.args(0))
    session.marked_items.append(item.unique_id)

    return ''


@auth.requires(
    lambda: auth.has_permission('update', db.desk, request.args(0)))
def edit():
    desk = db.desk(request.args(0))
    session.desk_id = desk.id

    db.desk.item_list.readable = False
    db.desk.item_list.writable = False
    form = SQLFORM(db.desk, record=desk, showid=False)

    if form.process().accepted:
        redirect(URL('index', args=[desk.id]))

    return locals()


@auth.requires(
    lambda: auth.has_permission('update', db.desk, request.args(0)))
def delete():
    desk = db.desk(request.args(0))
    session.desk_id = desk.id

    db.desk.item_list.readable = False
    db.desk.item_list.writable = False
    form = SQLFORM.confirm(
        T("Are you sure?"),
        {T('Cancel'): URL('index', args=[desk.id])})

    if form.accepted:
        # empty move all the items in the desk to the owners desk
        for item_id in desk.item_list:
            item = db.item(item_id)
            owner = db.auth_user(item.created_by)
            owner_desk = application.getUserDesk(user=owner)
            owner_desk_items = owner_desk.item_list
            owner_desk_items.append(item_id)
            owner_desk.update_record(item_list=owner_desk_items)

        # remove desk from org
        org = db(
            db.organization.desks.contains(desk.id)
        ).select().first()
        desk_list = org.desks
        desk_list.remove(desk.id)
        org.update_record(desks=desk_list)
        # delete the desk from db.
        del db.desk[desk.id]
        # cleanup context
        session.desk_id = None
        # go to org view
        redirect(URL('org','view', args=[org.id]))

    return locals()


@auth.requires(
    lambda: auth.has_permission('update', db.desk, request.args(0)))
def users():
    desk = db.desk(request.args(0))
    session.desk_id = desk.id

    org = db.organization(session.org_id)

    if request.args(1):
        my_user = db.auth_user(request.args(1))

        fld_read_desk = Field('read_desk', 'boolean')
        fld_read_desk.label = T("Read '%s' content", (desk.name,))
        fld_read_desk.comment = T(
            "Allow the user read only access to the desk item list.")
        fld_read_desk.default = auth.has_permission(
            'read', db.desk, desk.id, my_user.id)

        fld_update_items = Field('update_items', 'boolean')
        fld_update_items.label = T("Read/Update items in '%s'", (desk.name,))
        fld_update_items.comment = T(
            "Allow the user make modifications to the items in the desk.")
        fld_update_items.default = auth.has_permission(
            'update_items', db.desk, desk.id, my_user.id)

        fld_push_items = Field('push_items', 'boolean')
        fld_push_items.label = T("Push items into '%s'", (desk.name,))
        fld_push_items.comment = T(
            """Allow the user move items into the desk."""
        )
        fld_push_items.default = auth.has_permission(
            'push_items', db.desk, desk.id, my_user.id)

        fld_update_desk = Field('update_desk', 'boolean')
        fld_update_desk.label = T("Update/Manage '%s'", (desk.name,))
        fld_update_desk.comment = T(
            """
            Allow the user to manage/administrate this desk. Use with caution.
            """
        )
        fld_update_desk.default = auth.has_permission(
            'update', db.desk, desk.id, my_user.id)

        form = SQLFORM.factory(
            fld_read_desk,
            fld_update_items,
            fld_push_items,
            fld_update_desk,
            table_name='desk_perms'
        )

        if form.process().accepted:
            if form.vars.read_desk:
                # give perm
                auth.add_permission(
                    auth.user_group(my_user.id), 'read', db.desk, desk.id)
            else:
                auth.del_permission(
                    auth.user_group(my_user.id), 'read', db.desk, desk.id)

            if form.vars.update_items:
                # give perm
                auth.add_permission(
                    auth.user_group(my_user.id), 'update_items', db.desk,
                    desk.id)
            else:
                auth.del_permission(
                    auth.user_group(my_user.id), 'update_items', db.desk,
                    desk.id)

            if form.vars.push_items:
                # give perm
                auth.add_permission(
                    auth.user_group(my_user.id), 'push_items', db.desk,
                    desk.id)
            else:
                auth.del_permission(
                    auth.user_group(my_user.id), 'push_items', db.desk,
                    desk.id)

            if form.vars.update_desk:
                # give perm
                auth.add_permission(
                    auth.user_group(my_user.id), 'update_desk', db.desk,
                    desk.id)
            else:
                auth.del_permission(
                    auth.user_group(my_user.id), 'update_desk', db.desk,
                    desk.id)

            redirect(URL('desk', 'users', args=[desk.id]))

        response.view = "desk/user_perms.html"
    else:
        # select user view
        query = (db.auth_user.id > 0)
        query &= (db.auth_user.id.belongs(org.users))

        my_users = db(query).select()

    return locals()


@auth.requires(
    lambda: auth.has_permission('update', db.organization, session.org_id))
def create():
    org = db.organization(session.org_id)
    tbl = db.desk
    tbl.item_list.readable = False
    tbl.item_list.writable = False
    tbl.name.requires = IS_NOT_EMPTY()

    form = SQLFORM(db.desk)
    form.add_button(T('Cancel'), URL('org', 'view', args=[org.id]))

    if form.process().accepted:
        # add the new desk to the org list
        desk_id = form.vars.id
        # add current users as the one with permission to update manage
        # this desk
        auth.add_permission(
            auth.user_group(auth.user.id),
            'update',
            db.desk,
            desk_id)
        desk_list = org.desks
        desk_list.insert(0, desk_id)
        org.update_record(desks=desk_list)
        # return to the org desk list
        redirect(URL('org', 'view', args=[org.id]))

    return locals()
