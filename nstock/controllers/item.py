# -*- coding: utf-8 -*-
if False:
    from gluon import redirect, current, Field, HTTP
    from gluon import A, CAT, SPAN, SQLFORM, URL, IS_IN_SET
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T
    from db import auth, db
    from dc import application


@auth.requires(lambda: application.canReadItem(request.args(0)))
def index():
    """
    Make it the same as all_items or search views but showing only one item.
    """
    item = application.getItemByUUID(request.args(0))

    return locals()


@auth.requires(lambda: application.canUpdateItem(request.args(0)))
def meta():
    """
    Edit/Show item metadata info
    """
    item = application.getItemByUUID(request.args(0))

    if item is None:
        raise HTTP(404)

    contentType = application.getContentType(item.item_type)
    l_names = [
        (r.language_tag, r.english_name) for r in db(
            db.languages.id > 0
        ).select(orderby=db.languages.english_name)
    ]
    db.item.language_tag.requires = IS_IN_SET(
        l_names,
        zero=None
    )

    # issue #5 hidde some fields from metadata
    db.item.provider.readable = False
    db.item.provider.writable = False
    db.item.provider_service.readable = False
    db.item.provider_service.writable = False
    db.item.copyright_holder.readable = False
    db.item.copyright_holder.writable = False
    db.item.copyright_url.readable = False
    db.item.copyright_url.writable = False
    db.item.copyright_notice.readable = False
    db.item.copyright_notice.writable = False
    db.item.pubstatus.readable = False
    db.item.pubstatus.writable = False

    form = SQLFORM(db.item, record=item)

    if form.process().accepted:
        # session.flash = "Done !"
        # send an email to all the users who has access to this item
        application.notifyChanges(item.unique_id)
        application.indexItem(item.unique_id)
        if request.ajax:
            response.js = "$('#metaModal').modal('hide');"
        else:
            redirect(application.getItemURL(item.unique_id))

    return locals()


@auth.requires(lambda: application.canReadItem(request.args(0)))
def changelog():
    """
    Show item change log over the time
    """
    item = application.getItemByUUID(request.args(0))
    if item is None:
        raise HTTP(404)

    query = (db.item_archive.current_record == item.id)
    db.item_archive.modified_on.label = T('Date & Time')
    db.item_archive.modified_on.readable = True
    db.item_archive.modified_by.label = T('User')
    db.item_archive.modified_by.readable = True
    fields = [
        db.item_archive.modified_on,
        db.item_archive.modified_by
    ]

    def gen_links(row):
        diff = A(
            SPAN(_class="glyphicon glyphicon-random"),
            _href=URL(
                'diff',
                args=[item.unique_id, row.id]),
            _class="btn btn-default",
            _title=T("Differences"),
        )

        return CAT(diff)

    links = [dict(header='', body=gen_links)]

    changes = SQLFORM.grid(
        query,
        orderby=[~db.item_archive.modified_on],
        fields=fields,
        args=request.args[:1],
        create=False, editable=False, details=False, deletable=False,
        searchable=False,
        csv=False,
        links=links,
    )

    return dict(item=item, changes=changes)


@auth.requires(lambda: application.canReadItem(request.args(0)))
def diff():
    """
    Show the diff betwen the actual item and the archive one
    """
    item = application.getItemByUUID(request.args(0))
    if item is None:
        raise HTTP(404)
    item_archive = db.item_archive(request.args(1))
    if item_archive is None:
        raise HTTP(503)

    fields = []
    fields_archived = []

    # allow view of administrative metadata
    db.item.modified_by.readable = True
    db.item.modified_on.readable = True
    db.item_archive.modified_by.readable = True
    db.item_archive.modified_on.readable = True

    for f in db.item:
        if item[f.name] != item_archive[f.name]:
            f.comment = None
            fields.append(f)
            db.item_archive[f.name].comment = None
            fields_archived.append(db.item_archive[f.name])

    # build two readonly forms
    form_actual = SQLFORM.factory(
        *fields,
        record=item,
        readonly=True,
        showid=False,
        formstyle='divs'
        )
    form_archive = SQLFORM.factory(
        *fields_archived,
        record=item_archive,
        readonly=True,
        showid=False,
        formstyle='divs')

    return dict(item=item, form_actual=form_actual, form_archive=form_archive)


@auth.requires(lambda: application.canUpdateItem(request.args(0)))
def share():
    """
    Show the list of desk to with the item can be push
    """
    item = application.getItemByUUID(request.args(0))
    if item is None:
        raise HTTP(404)

    query = (db.desk.id != session.desk_id)
    query &= auth.accessible_query('push_items', db.desk)

    posible_desk = db(query).select()

    fld_to_desk = Field('to_desk', 'integer')
    fld_to_desk.label = T("Push to")
    fld_to_desk.comment = T("Select where to push the item")
    fld_to_desk.requires = IS_IN_SET(
        [(desk.id, desk.name) for desk in posible_desk]
    )
    form = SQLFORM.factory(
        fld_to_desk,
        submit_button=T("Send"),
        table_name='share')
    if form.process().accepted:
        # send the item to the selected desk
        ct = application.getContentType(item.item_type)
        ct.shareItem(item.unique_id, session.desk_id, form.vars.to_desk)
        response.js = "$('#metaModal').modal('hide');"

    return locals()
