
db.define_table('music',
                Field('name',required=True),
                Field('filename','upload',required=True),
                auth.signature)

