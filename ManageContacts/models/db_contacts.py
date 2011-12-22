# coding: utf8

db.define_table('company',
                Field('name',notnull=True,unique=True),
                format='%(name)s')
db.define_table('contact',
                Field('name',notnull=True),
                Field('company','reference company'),
                Field('picture','upload'),
                Field('email',requires=IS_EMAIL()),
                Field('phone_number',requires=IS_MATCH('[\d\-\(\) ]+')),
                Field('address'),
                format='%(name)s')
db.define_table('log',
                Field('body','text',notnull=True),
                Field('posted_on','datetime'),
                Field('contact','reference contact'))
