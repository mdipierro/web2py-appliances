# -*- coding: utf-8 -*-
from gluon.storage import Storage
from PIL import Image
from tempfile import NamedTemporaryFile
import os

if False:
    from gluon import URL, IMG, CAT, SQLFORM, A, SPAN
    from gluon import current, redirect
    T = current.T
    request = current.request
    response = current.response
    session = current.session
    from db import db, auth
    from dc import application


@auth.requires(lambda: application.canUpdateItem(request.args(0)))
def index():
    item = application.getItemByUUID(request.args(0))
    content = db.plugin_photoset_content(item_id=item.id)

    return locals()


@auth.requires(lambda: application.canReadItem(request.args(0)))
def view_photoset():
    item = application.getItemByUUID(request.args(0))
    content = db.plugin_photoset_content(item_id=item.unique_id)
    photos = content.photoset
    if not photos:
        photos = []
    return locals()


@auth.requires(lambda: application.canReadItem(request.args(0)))
def preview_photo():
    item = application.getItemByUUID(request.args(0))
    photo = db.plugin_photoset_photo(request.args(1))
    return IMG(
        _src=URL('default', 'download', args=[photo.picture]),
        _class="img-responsive center-block",
        _alt=item.slugline,
    )


@auth.requires(lambda: application.canUpdateItem(request.args(0)))
def delete_photo():
    item = application.getItemByUUID(request.args(0))
    content = db.plugin_photoset_content(item_id=item.unique_id)
    photo = db.plugin_photoset_photo(request.args(1))

    content.photoset.remove(photo.id)
    del db.plugin_photoset_photo[photo.id]
    content.update_record()
    application.notifyChanges(item.unique_id)

    return CAT('')


@auth.requires(lambda: application.canUpdateItem(request.args(0)))
def edit_form():
    item = application.getItemByUUID(request.args(0))
    content = db.plugin_photoset_content(item_id=item.unique_id)

    db.plugin_photoset_content.photoset.readable = False
    db.plugin_photoset_content.photoset.writable = False
    db.plugin_photoset_content.item_id.readable = False
    db.plugin_photoset_content.item_id.writable = False

    form = SQLFORM(
        db.plugin_photoset_content,
        record=content,
        showid=False,
        submit_button=T('Save')
    )

    if form.process().accepted:
        application.notifyChanges(item.unique_id)
        application.indexItem(item.unique_id)
        response.flash = T('Saved')

    return form


@auth.requires(lambda: application.canReadItem(request.args(0)))
def changelog():
    """
    Show item change log over the time
    """
    item = application.getItemByUUID(request.args(0))
    content = db.plugin_photoset_content(item_id=item.unique_id)

    query = (db.plugin_photoset_content_archive.current_record == content.id)
    db.plugin_photoset_content_archive.modified_on.label = T('Date & Time')
    db.plugin_photoset_content_archive.modified_on.readable = True
    db.plugin_photoset_content_archive.modified_by.label = T('User')
    db.plugin_photoset_content_archive.modified_by.readable = True
    fields = [
        db.plugin_photoset_content_archive.modified_on,
        db.plugin_photoset_content_archive.modified_by
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
        orderby=[~db.plugin_photoset_content_archive.modified_on],
        fields=fields,
        args=request.args[:1],
        create=False, editable=False, details=False, deletable=False,
        searchable=False,
        csv=False,
        links=links,
    )

    return locals()


@auth.requires(lambda: application.canReadItem(request.args(0)))
def diff():
    item = application.getItemByUUID(request.args(0))
    content = db.plugin_photoset_content(item_id=item.unique_id)
    archive = db.plugin_photoset_content_archive(request.args(1))

    fields = []
    fields_archived = []
    fields_names = []

    for f in db.plugin_photoset_content:
        # if values diff
        if content[f.name] != archive[f.name]:
            fields_names.append(f.name)
            f.comment = None
            fields.append(f)
            db.plugin_photoset_content_archive[f.name].comment = None
            fields_archived.append(db.plugin_photoset_content_archive[f.name])

    # build two readonly forms
    form_actual = SQLFORM.factory(
        *fields,
        record=content,
        readonly=True,
        showid=False,
        formstyle='divs'
        )
    form_archive = SQLFORM.factory(
        *fields_archived,
        record=archive,
        readonly=True,
        showid=False,
        formstyle='divs')

    return locals()


@auth.requires_login()
def create():
    fields = []

    fld_headline = db.item.headline
    fields.extend([fld_headline, db.item.keywords, db.item.genre])
    fdl_item_type = db.item.item_type
    fdl_item_type.writable = False
    fdl_item_type.readable = False
    fdl_item_type.default = 'photoset'

    form = SQLFORM.factory(
        *fields,
        table_name='plugin_photo_set'  # to allow the correct form name
    )

    if form.process(dbio=False).accepted:
        # item_id = CT_REG.photoset.create_item(form.vars)
        item_id = application.createItem('photoset', form.vars)
        form.vars.item_id = item_id
        if session.plugin_photoset:
            form.vars.photoset = session.plugin_photoset.photos
        else:
            form.vars.phoset = []
        db.plugin_photoset_content.insert(
            **db.plugin_photoset_content._filter_fields(
                form.vars
            )
        )
        application.indexItem(item_id)
        session.plugin_photoset = None
        redirect(URL('default', 'index.html'))

    return locals()


@auth.requires_login()
def upload_photo():
    """upload one or more photos"""
    if not session.plugin_photoset:
        session.plugin_photoset = Storage()
        session.plugin_photoset.photos = []

    for r in request.vars:
        if r == "qqfile":
            filename = request.vars.qqfile
            photo_id = db.plugin_photoset_photo.insert(
                picture=db.plugin_photoset_photo.picture.store(
                    request.body, filename
                )
            )
            # generate the thumbnail
            photo = db.plugin_photoset_photo(photo_id)
            (filename, stream) = db.plugin_photoset_photo.picture.retrieve(
                photo.picture
            )
            filename = stream.name
            im = Image.open(filename)
            # --------------------------------
            size = (200, 200)
            im.thumbnail(size)
            fl = NamedTemporaryFile(suffix=".jpg", delete=True)
            fl.close()
            im.save(fl.name, "JPEG")
            thumb = db.plugin_photoset_photo.thumbnail.store(
                open(fl.name, 'rb'), fl.name)
            photo.update_record(thumbnail=thumb)
            os.unlink(fl.name)  # cleanup
            # if a photoset is given add this photo to the set
            if request.args(0):
                item = application.getItemByUUID(request.args(0))
                photoset = db.plugin_photoset_content(item_id=item.unique_id)
                if photoset.photoset is None:
                    photoset.photoset = [photo_id]
                else:
                    photoset.photoset.append(photo_id)
                photoset.update_record()
            else:
                # in the create stage, i guess
                session.plugin_photoset.photos.append(photo_id)

            return response.json({'success': 'true'})
