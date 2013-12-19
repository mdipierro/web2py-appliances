# coding: utf8

def _():
    plugins.comments.db.define_table(
        'plugin_comments_post',
        Field('tablename',writable=False,readable=False),
        Field('record_id','integer',writable=False,readable=False),
        Field('body','text',requires=IS_NOT_EMPTY()),
        auth.signature)
_()
