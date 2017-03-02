# -*- coding: utf-8 -*-
if False:
    from gluon import current, URL, SQLFORM, redirect
    from gluon import IS_NOT_EMPTY, Field, IS_EMAIL
    from gluon import IS_NOT_IN_DB
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T
    from db import db, auth


@auth.requires_login()
def index():
    """
    Show the user the organizations he/she can access
    """
    query = (db.organization.id > 0)
    query &= (
        auth.accessible_query('read', db.organization) |
        auth.accessible_query('update', db.organization))

    orgs = db(query).select(db.organization.ALL)

    return locals()


@auth.requires(
    auth.has_permission('read', db.organization, request.args(0)) or
    auth.has_permission('update', db.organization, request.args(0))
)
def view():
    """
    Show the list of desks in this org
    """
    org = db.organization(request.args(0))
    session.org_id = org.id
    return locals()


@auth.requires(auth.has_permission('update', db.organization, request.args(0)))
def edit():
    org = db.organization(request.args(0))
    tbl = db.organization
    tbl.users.readable = False
    tbl.users.writable = False
    tbl.desks.readable = False
    tbl.desks.writable = False
    tbl.name.requires = [IS_NOT_EMPTY()]

    # edit form
    form = SQLFORM(db.organization, record=org, showid=False)
    if form.process().accepted:
        redirect(URL('view', args=[org.id]))

    return locals()


@auth.requires(auth.has_permission('update', db.organization, request.args(0)))
def members():
    org = db.organization(request.args(0))

    if not request.args(1):
        fld_email = Field('email', 'string', label=T("Email"))
        fld_email.requires = IS_EMAIL()

        form = SQLFORM.factory(
            fld_email,
            formstyle='bootstrap3_inline',
            submit_button=T("Add user"),
            table_name='members')

        if form.process().accepted:
            u = db.auth_user(email=form.vars.email)
            if u is not None:
                # create new share
                if u.id in org.users:
                    form.errors.email = T(
                        "The user is already in the organization")
                else:
                    user_list = org.users
                    user_list.insert(0, u.id)
                    org.update_record(users=user_list)
                    g_id = auth.user_group(u.id)
                    auth.add_permission(g_id, 'read', db.organization, org.id)
            else:
                # no user with that email
                response.flash = ""
                form.errors.email = T("The user don't exists on this system")
    elif request.args(1) == 'delete':
        # remove the user on args(2) from the org members list
        # TODO: remove else any perms on the org desks
        user_to_remove = db.auth_user(request.args(2))
        if user_to_remove is not None:
            user_list = org.users
            user_list.remove(user_to_remove.id)
            org.update_record(users=user_list)
            # remove perms over the org
            auth.del_permission(
                auth.user_group(user_to_remove.id),
                'read',
                db.organization,
                org.id)
            # remove, also, all rights over the desks in the org.
            desk_perms = [
                'read_desk', 'update_items', 'push_items', 'update_desk']
            for desk_id in org.desks:
                for perm in desk_perms:
                    auth.del_permission(
                        auth.user_group(user_to_remove.id),
                        perm,
                        db.desk,
                        desk_id
                    )
        redirect(URL('org', 'members', args=[org.id]))

    return locals()


@auth.requires_login()
def create():
    """Create a new organization"""
    tbl = db.organization
    tbl.users.readable = False
    tbl.users.writable = False
    tbl.desks.readable = False
    tbl.desks.writable = False
    tbl.name.requires = [
        IS_NOT_EMPTY(
            error_message=T("Cannot be empty")
        ),
        IS_NOT_IN_DB(
            db,
            'organization.name',
            error_message=T(
                "An Organization witch that name is allready in nStock"))]

    form = SQLFORM(tbl)
    form.add_button(T('Cancel'), URL('index'))

    if form.process().accepted:
        # add the new organization
        g_id = auth.user_group(auth.user.id)
        # give the user all perms over this org
        auth.add_permission(g_id, 'update', tbl, form.vars.id)
        auth.add_permission(g_id, 'read', tbl, form.vars.id)
        auth.add_permission(g_id, 'delete', tbl, form.vars.id)
        redirect(URL('index'))

    return locals()
