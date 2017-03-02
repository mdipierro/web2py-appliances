# -*- coding: utf-8 -*-
if False:
    from gluon import SQLFORM, URL, A, SPAN, CAT
    from gluon import current, redirect, HTTP
    request = current.request
    response = current.response
    T = current.T
    from db import db, auth
    # from dc import CT_REG
    from dc import application


@auth.requires(lambda: application.canUpdateItem(request.args(0)))
def index():
    """
    Edit content
    """
    item = application.getItemByUUID(request.args(0))
    if item is None:
        raise HTTP(404)

    content = db.plugin_text_text(item_id=item.unique_id)

    form = SQLFORM(
        db.plugin_text_text,
        record=content,
        showid=False,
        submit_button=T('Save'))

    if form.process().accepted:
        application.notifyChanges(item.unique_id)
        application.indexItem(item.unique_id)
        redirect(application.getItemURL(item.unique_id))
        response.flash = T('Done')

    return dict(form=form, item=item, content=content)


@auth.requires(lambda: application.canReadItem(request.args(0)))
def diff():
    item = application.getItemByUUID(request.args(0))
    if item is None:
        raise HTTP(404)
    content = db.plugin_text_text(item_id=item.unique_id)
    archive = db.plugin_text_text_archive(request.args(1))

    fields = []
    fields_archived = []
    fields_names = []

    for f in db.plugin_text_text:
        # if values diff
        if content[f.name] != archive[f.name]:
            fields_names.append(f.name)
            f.comment = None
            fields.append(f)
            db.plugin_text_text_archive[f.name].comment = None
            fields_archived.append(db.plugin_text_text_archive[f.name])

    # build two readonly forms
    form_actual = SQLFORM.factory(
        *fields,
        record=content,
        readonly=True,
        showid=False,
        formstyle='divs'
        )
    form_archive = SQLFORM.factory(
        *fields,
        record=archive,
        readonly=True,
        showid=False,
        formstyle='divs')

    return locals()


@auth.requires(lambda: application.canReadItem(request.args(0)))
def changelog():
    """
    Show item change log over the time
    """
    item = application.getItemByUUID(request.args(0))
    if item is None:
        raise HTTP(404)
    content = db.plugin_text_text(item_id=item.unique_id)

    query = (db.plugin_text_text_archive.current_record == content.id)
    db.plugin_text_text_archive.modified_on.label = T('Date & Time')
    db.plugin_text_text_archive.modified_on.readable = True
    db.plugin_text_text_archive.modified_by.label = T('User')
    db.plugin_text_text_archive.modified_by.readable = True
    fields = [
        db.plugin_text_text_archive.modified_on,
        db.plugin_text_text_archive.modified_by
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
        orderby=[~db.plugin_text_text_archive.modified_on],
        fields=fields,
        args=request.args[:1],
        create=False, editable=False, details=False, deletable=False,
        searchable=False,
        csv=False,
        links=links,
    )

    return locals()


@auth.requires_login()
def create():
    """
    Show the creation form of the text item.
    """

    fields = [
        db.item.headline,
        db.item.keywords,
        db.item.genre,
        db.item.item_type,
        db.plugin_text_text.body
    ]
    db.item.item_type.default = 'text'
    db.item.item_type.writable = False
    db.item.item_type.readable = False

    form = SQLFORM.factory(*fields)

    if form.process().accepted:
        item_id = application.createItem('text', form.vars)
        form.vars.item_id = item_id
        db.plugin_text_text.insert(
            **db.plugin_text_text._filter_fields(form.vars))
        application.indexItem(item_id)
        redirect(URL('default', 'index.html'))

    return locals()
