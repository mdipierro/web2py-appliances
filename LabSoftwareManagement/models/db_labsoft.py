db.define_table('software',
                Field('name',unique=True),
                Field('vendor'),
                Field('description'),
                Field('platform',requires=IS_IN_SET(('Windows','Mac'))),
                auth.signature,
                format='%(name)s')

db.define_table('lab',
                Field('name',unique=True),
                Field('location'),
                Field('info',represent=lambda a,b:MARKMIN(a)),
                auth.signature,
                format='%(name)s')

db.define_table('unit',
                Field('name',unique=True),
                auth.signature,
                format='%(name)s')

db.define_table('requirement',
                Field('unit','reference unit'),
                Field('software','reference software'),
                Field('labs','list:reference lab'),
                auth.signature)

                
for table in db:
    if 'is_active' in table.fields():
        table.is_active.writable=table.is_active.readable=False
