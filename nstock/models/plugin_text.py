# -*- coding: utf-8 -*-
from plugin_text.content_text import ContentText
from plugin_ckeditor import CKEditor
from gluon import Field, IS_NOT_EMPTY
from gluon.tools import PluginManager

if False:
    from gluon import current
    response = current.response
    request = current.request
    T = current.T
    from db import db, auth


# define tables of this plugin
def _():
    plugins = PluginManager('text', app=None)
    if plugins.text.app is not None:
        # this will register the content/type on the application
        plugins.text.app.registerContentType('text', ContentText())
        if not hasattr(db, 'plugin_text_text'):
            # configure ckeditor
            editor = CKEditor(db=db)
            # definimos la BD
            tbl = db.define_table(
                'plugin_text_text',
                Field('byline', 'string', length=250, default=''),
                Field('body', 'text', label=T('Content')),
                Field('item_id', 'string', length=64),
                auth.signature,
            )
            tbl.byline.label = T('By line')
            tbl.item_id.readable = False
            tbl.item_id.writable = False
            tbl.body.requires = IS_NOT_EMPTY()
            tbl.body.widget = editor.widget

            # enable record  versioning
            tbl._enable_record_versioning()

    return
_()
