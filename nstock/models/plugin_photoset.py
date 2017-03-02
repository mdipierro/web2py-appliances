# -*- coding: utf-8 -*-
from plugin_photoset.content_photoset import ContentPhotoset
from gluon.tools import PluginManager
from plugin_ckeditor import CKEditor

if False:
    from gluon import current, Field
    response = current.response
    request = current.request
    T = current.T
    from db import db, auth


def _():
    plugins = PluginManager('photoset', app=None)
    if plugins.photoset.app is not None:
        plugins.photoset.app.registerContentType('photoset', ContentPhotoset())
        editor = CKEditor(db=db)
        if not hasattr(db, 'plugin_photoset_photo'):
            db.define_table(
                'plugin_photoset_photo',
                Field(
                    'thumbnail', 'upload',
                    uploadseparate=True,
                    autodelete=True,
                    default=None
                ),
                Field(
                    'picture', 'upload',
                    uploadseparate=True,
                    autodelete=True
                ),
            )

        if not hasattr(db, 'plugin_photoset_content'):
            tbl = db.define_table(
                'plugin_photoset_content',
                Field('credit_line', 'string', length=250, default=''),
                Field(
                    'description', 'text',
                    label=T('Description'),
                    default=''
                ),
                Field('photoset', 'list:reference plugin_photoset_photo'),
                Field('item_id', 'string', length=64),
                auth.signature,
            )
            tbl.credit_line.label = T("Credit line")
            tbl.description.label = T('Description')
            tbl.description.widget = editor.widget
            tbl._enable_record_versioning()
_()
