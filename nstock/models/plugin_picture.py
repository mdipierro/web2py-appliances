# -*- coding: utf-8 -*-

from plugin_picture.content_picture import ContentPicture
from gluon.tools import PluginManager
from plugin_ckeditor import CKEditor

if False:
    from gluon import current
    from gluon import Field, IS_NOT_EMPTY, IS_IMAGE
    response = current.response
    request = current.request
    T = current.T
    from db import db, auth


def _():
    plugins = PluginManager('picture', app=None)
    # this will register the content/type on the application
    if plugins.picture.app is not None:
        editor = CKEditor(db=db)
        plugins.picture.app.registerContentType('picture', ContentPicture())
        if not hasattr(db, 'plugin_picture_rendition'):
            tbl = db.define_table(
                'plugin_picture_rendition',
                Field(
                    'picture', 'upload', uploadseparate=True, autodelete=True
                ),
                Field('purpose', 'string', length=50, default='raw'),
                Field(
                    'height', 'integer', default=0, readable=False,
                    writable=False
                ),
                Field(
                    'width', 'integer', default=0, readable=False,
                    writable=False
                ),
                Field(
                    'color', 'string', length=20, readable=False,
                    writable=False
                ),
                Field(
                    'format', 'string', length=10, readable=False,
                    writable=False
                )
            )
            tbl.purpose.comment = T('''
            It may contain any value but it is recommended to use one of the
            values: raw, web, thumbnail, print
            ''')
            tbl.purpose.label = T('Purpose')
            tbl.height.label = T('Height')
            tbl.width.label = T('Width')
            tbl.color.label = T('Color space')
            tbl.format.label = T('Format')
            tbl.format.comment = T('Automatic form PIL')
            tbl.picture.label = T('Picture')
            tbl.picture.requires = [IS_IMAGE(), IS_NOT_EMPTY()]

        if not hasattr(db, 'plugin_picture_info'):
            # definimos la BD
            tbl = db.define_table(
                'plugin_picture_info',
                Field('credit_line', 'string', length=250, default=''),
                Field(
                    'description', 'text',
                    label=T('Description'),
                    default=''
                ),
                Field(
                    'caption', 'string',
                    length=250,
                    default=''
                ),
                Field(
                    'thumbnail', 'upload',
                    uploadseparate=True,
                    autodelete=True,
                    default=None
                ),
                Field('renditions', 'list:reference plugin_picture_rendition'),
                Field('item_id', 'string', length=64),
                auth.signature,
            )
            tbl.credit_line.label = T("Credit line")
            tbl.description.label = T('Description')
            tbl.description.widget = editor.widget
            tbl.caption.label = T("Caption")
            tbl.renditions.label = T("Renditions")
            tbl.item_id.readable = False
            tbl.item_id.writable = False

            # enable record  versioning
            tbl._enable_record_versioning()

    return
_()
