db.define_table('chat_line',
    Field('name'),
    Field('description','text',default=''),
    Field('created_on','datetime',default=timestamp),
    Field('owner',db.auth_user))

db.chat_line.name.requires=IS_NOT_EMPTY()
db.chat_line.access_types=['none','read','read/chat']
db.chat_line.public_fields=['name','description']

db.define_table('message',
    Field('chat_line',db.chat_line),
    Field('body','text',default=''),
    Field('posted_on','datetime',default=timestamp),
    Field('posted_by',db.auth_user))

db.message.body.requires=IS_NOT_EMPTY()
