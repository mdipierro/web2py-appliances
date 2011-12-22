# coding: utf8

db.define_table('category',
                Field('name',notnull=True,unique=True),
                format='%(name)s')
db.define_table('news',
                Field('title',notnull=True),
                Field('link',requires=IS_URL()),
                Field('category','reference category',readable=False,writable=False),
                Field('votes','integer',readable=False,writable=False),
                Field('posted_on','datetime',readable=False,writable=False),
                Field('posted_by','reference auth_user',readable=False,writable=False),
                format='%(title)s')
db.define_table('comment',
                Field('news','reference news',readable=False,writable=False),
                Field('parent_comment','reference comment',readable=False,writable=False),
                Field('body','text',notnull=True),
                Field('posted_on','datetime',readable=False,writable=False),
                Field('posted_by','reference auth_user',readable=False,writable=False))
db.define_table('vote',
                Field('news','reference news'),
                Field('value','integer'),
                Field('posted_on','datetime',readable=False,writable=False),
                Field('posted_by','reference auth_user',readable=False,writable=False))
