# -*- coding: utf-8 -*-

import os
from gluon import *
from plugin_ckeditor import CKEditor
current.plugin_ckeditor = CKEditor()
current.plugin_ckeditor.define_tables()
db = current.plugin_ckeditor.db


def upload():
    (new_filename, old_filename, length, mime_type) = current.plugin_ckeditor.handle_upload()
    title = os.path.splitext(old_filename)[0]
    result = current.plugin_ckeditor.settings.table_upload.validate_and_insert(
        title=title,
        filename=old_filename,
        upload=new_filename,
        flength=length,
        mime_type=mime_type,
        user_id=session.auth.user.id,
        created_on=request.now
    )

    text = ''
    url = URL('default', 'download', args=[new_filename])

    if not result.id:
        text = result.errors

    return dict(text=text, cknum=request.vars.CKEditorFuncNum, url=url)


def browse():
    table_upload = current.plugin_ckeditor.settings.table_upload
    browse_filter = current.plugin_ckeditor.settings.browse_filter
    set = db(table_upload.user_id == session.auth.user.id)
    for key, val in browse_filter.items():
        if value[0] == '<':
            set = set(table_upload[key] < value[1:])
        elif value[0] == '>':
            set = set(table_upload[key] > value[1:])
        elif value[0] == '!':
            set = set(table_upload[key] != value[1:])
        else:
            set = set(table_upload[key] == value)

    rows = set.select(orderby=table_upload.title)
    #aditional images
    return dict(rows=rows, cknum=request.vars.CKEditorFuncNum, article_images=[])


def delete():
    filename = request.args(0)
    if not filename:
        raise HTTP(401, 'Required argument filename missing.')

    table_upload = current.plugin_ckeditor.settings.table_upload
    db(table_upload.upload == filename).delete()

    # delete the file from storage
    path = os.path.join(request.folder, 'uploads', filename)
    os.unlink(path)
