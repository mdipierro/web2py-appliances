# -*- coding: utf-8 -*-
from PIL import Image
from tempfile import NamedTemporaryFile
import os

if False:
    from gluon import SQLFORM, CAT, A, SPAN, URL, IS_IMAGE
    from gluon import current, redirect
    request = current.request
    response = current.response
    T = current.T
    from db import db, auth
    from dc import application


@auth.requires(lambda: application.canUpdateItem(request.args(0)))
def index():
    """
    Edit content
    """
    item = application.getItemByUUID(request.args(0))

    db.plugin_picture_info.thumbnail.readable = False
    db.plugin_picture_info.thumbnail.writable = False
    db.plugin_picture_info.renditions.readable = False
    db.plugin_picture_info.renditions.writable = False

    content = db.plugin_picture_info(item_id=item.unique_id)

    form = SQLFORM(
        db.plugin_picture_info,
        record=content,
        showid=False,
        submit_button=T('Save'))

    if form.process().accepted:
        application.notifyChanges(item.unique_id)
        application.indexItem(item.unique_id)
        response.flash = None

    return dict(form=form, item=item, content=content)


@auth.requires(lambda: application.canUpdateItem(request.args(0)))
def delete_rendition():
    item = application.getItemByUUID(request.args(0))
    content = db.plugin_picture_info(item_id=item.unique_id)
    rend = db.plugin_picture_rendition(request.args(1))

    if item and content and rend:
        # remove rendition
        # update content.renditions
        # update content db record
        r_id = rend.id
        del db.plugin_picture_rendition[r_id]
        content.renditions.remove(r_id)
        content.update_record()

    return CAT('')


@auth.requires(lambda: application.canReadItem(request.args(0)))
def diff():
    item = application.getItemByUUID(request.args(0))
    content = db.plugin_picture_info(item_id=item.unique_id)
    archive = db.plugin_picture_info_archive(request.args(1))

    fields = []
    fields_archived = []
    fields_names = []

    for f in db.plugin_picture_info:
        # if values diff
        if content[f.name] != archive[f.name]:
            fields_names.append(f.name)
            f.comment = None
            fields.append(f)
            db.plugin_picture_info_archive[f.name].comment = None
            fields_archived.append(db.plugin_picture_info_archive[f.name])

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
    item = application.getItemByUUID(request.args(0))
    pic_info = db.plugin_picture_info(item_id=item.unique_id)

    query = (db.plugin_picture_info_archive.current_record == pic_info.id)
    db.plugin_picture_info_archive.modified_on.label = T('Date & Time')
    db.plugin_picture_info_archive.modified_on.readable = True
    db.plugin_picture_info_archive.modified_by.label = T('User')
    db.plugin_picture_info_archive.modified_by.readable = True
    fields = [
        db.plugin_picture_info_archive.modified_on,
        db.plugin_picture_info_archive.modified_by
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
        orderby=[~db.plugin_picture_info_archive.modified_on],
        fields=fields,
        args=request.args[:1],
        create=False, editable=False, details=False, deletable=False,
        searchable=False,
        csv=False,
        links=links,
    )

    return locals()


@auth.requires(lambda: application.canReadItem(request.args(0)))
def add_rendition():
    item = application.getItemByUUID(request.args(0))
    content = db.plugin_picture_info(item_id=item.unique_id)

    form = SQLFORM(db.plugin_picture_rendition)

    if form.process().accepted:
        r_id = form.vars.id
        rend = db.plugin_picture_rendition(r_id)
        (filename, stream) = db.plugin_picture_rendition.picture.retrieve(
            rend.picture)
        filename = stream.name
        im = Image.open(filename)
        # update rendition with image info
        rend.height = im.height
        rend.width = im.width
        rend.format = im.format
        rend.color = im.mode
        rend.update_record()
        # append this rendition to the item content
        content.renditions.append(r_id)
        content.update_record()
        redirect(application.getItemURL(item.unique_id))

    return locals()


@auth.requires_login()
def create():

    fields = []
    # i need the input of the based item fields
    fdl_headline = db.item.headline
    fields.append(fdl_headline)
    fields.append(db.item.keywords)
    fields.append(db.item.genre)
    fdl_item_type = db.item.item_type
    fdl_item_type.writable = False
    fdl_item_type.readable = False
    fdl_item_type.default = 'picture'

    # and the image for the first redition
    fld_redition = db.plugin_picture_rendition.picture
    fld_redition.uploadfolder = os.path.join(request.folder, 'uploads')
    fld_redition.label = T('Select the first rendition of the picture')
    fld_redition.comment = T("""
    Normally the raw version of the image. You may add other renditions as
    needed after form submition..
    """)
    fld_redition.requires = IS_IMAGE()
    fields.append(fld_redition)

    form = SQLFORM.factory(
        *fields,
        table_name='plugin_picture_rendition'  # to allow the correct form name
    )

    if form.process(dbio=False).accepted:
        # create the item
        item_id = application.createItem('picture', form.vars)
        # first rendition
        rend_id = db.plugin_picture_rendition.insert(
            **db.plugin_picture_rendition._filter_fields(form.vars)
        )
        form.vars.renditions = [rend_id]
        # generate the thumbnail
        rend = db.plugin_picture_rendition(rend_id)
        (filename, stream) = db.plugin_picture_rendition.picture.retrieve(
            rend.picture)
        filename = stream.name
        im = Image.open(filename)
        # update rendition with image info
        rend.width, rend.height = im.size
        rend.format = im.format
        rend.color = im.mode
        rend.update_record()
        # --------------------------------
        size = (500, 500)
        im.thumbnail(size)
        fl = NamedTemporaryFile(suffix=".jpg", delete=True)
        fl.close()
        im.save(fl.name, "JPEG")
        form.vars.thumbnail = db.plugin_picture_info.thumbnail.store(
            open(fl.name, 'rb'), fl.name)
        os.unlink(fl.name)  # cleanup
        # create the picture main content
        form.vars.item_id = item_id
        info_id = db.plugin_picture_info.insert(
            **db.plugin_picture_info._filter_fields(form.vars)
        )
        # register document for search
        application.indexItem(item_id)
        # --
        # redirect to the item
        redirect(URL('default', 'index'))

    return locals()
