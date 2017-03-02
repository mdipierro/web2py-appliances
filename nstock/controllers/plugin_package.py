# -*- coding: utf-8 -*-
if False:
    from gluon import CAT, SQLFORM, A, SPAN, URL
    from gluon import current, redirect
    request = current.request
    response = current.response
    session = current.session
    T = current.T
    from db import db, auth
    from dc import application


@auth.requires(lambda: application.canUpdateItem(request.args(0)))
def index():
    """
    Edit/Show package content
    """
    pkg_item = application.getItemByUUID(request.args(0))
    content = db.plugin_package_content(item_id=pkg_item.unique_id)

    form = SQLFORM(
        db.plugin_package_content,
        record=content,
        showid=False)

    if form.process().accepted:
        application.indexItem(pkg_item.unique_id)
        redirect(URL('default', 'index'))

    return locals()


@auth.requires(lambda: application.canReadItem(request.args(0)))
def diff():
    item = application.getItemByUUID(request.args(0))
    content = db.plugin_package_content(item_id=item.unique_id)
    archive = db.plugin_package_content_archive(request.args(1))
    return locals()


@auth.requires(lambda: application.canReadItem(request.args(0)))
def changelog():
    item = application.getItemByUUID(request.args(0))
    pkg_content = db.plugin_package_content(item_id=item.unique_id)
    query = (
        db.plugin_package_content_archive.current_record == pkg_content.id)
    db.plugin_package_content_archive.modified_on.label = T('Date & Time')
    db.plugin_package_content_archive.modified_on.readable = True
    db.plugin_package_content_archive.modified_by.label = T('User')
    db.plugin_package_content_archive.modified_by.readable = True
    fields = [
        db.plugin_package_content_archive.modified_on,
        db.plugin_package_content_archive.modified_by
    ]

    def gen_links(row):
        diff = A(SPAN(
            _class="glyphicon glyphicon-random"),
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
        orderby=[~db.plugin_package_content_archive.modified_on],
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
    if not session.marked_items:
        session.flash = T('You must mark some items first')
        redirect(URL('default', 'index'))

    fields = []
    # i need the input of the based item fields
    fdl_headline = db.item.headline
    fields.append(fdl_headline)
    fdl_keywords = db.item.keywords
    keywords_list = []
    for item_id in session.marked_items:
        _item = application.getItemByUUID(item_id)
        keywords_list.extend(_item.keywords)
    keywords_list = list(set(keywords_list))  # remove any dup
    fdl_keywords.default = keywords_list
    fields.append(fdl_keywords)
    fields.append(db.item.genre)
    fdl_item_type = db.item.item_type
    fdl_item_type.writable = False
    fdl_item_type.readable = False
    fdl_item_type.default = 'package'
    fields.append(db.plugin_package_content.description)

    form = SQLFORM.factory(
        *fields,
        table_name='plugin_package_item'  # to allow the correct file name
    )

    if form.process(dbio=False).accepted:
        form.vars.item_id = application.createItem('package', form.vars)
        form.vars.item_list = session.marked_items
        db.plugin_package_content.insert(
            **db.plugin_package_content._filter_fields(form.vars)
        )
        application.indexItem(form.vars.item_id)
        session.marked_items = []
        redirect(URL('default', 'index'))

    return locals()
