db.define_table('folder',
    Field('name'),
    Field('description','text',default=''),
    Field('keywords','string',length=128,default=''),
    Field('is_open','boolean',default=False),
    Field('created_on','datetime',default=timestamp),
    Field('owner',db.auth_user))

db.folder.name.requires=IS_NOT_EMPTY()
db.folder.access_types=['none','read','read/edit']
db.folder.public_fields=['name','description','keywords','is_open']

db.define_table('page',
    Field('folder',db.folder),
    Field('number','integer',default=0),
    Field('locked_on','integer',default=0),
    Field('locked_by','integer',default=0),
    Field('title'),
    Field('body','text',default=''),
    Field('readonly','boolean',default=False),
    Field('comments_enabled','boolean',default=False),
    Field('modified_on','datetime',default=timestamp),
    Field('modified_by',db.auth_user))

db.page.folder.requires=IS_IN_DB(db,'folder.id','%(id)s:%(name)s')
db.page.title.requires=IS_NOT_EMPTY()
db.page.public_fields=['title','body','readonly','comments_enabled']

db.define_table('old_page',
    Field('page',db.page),
    Field('title'),
    Field('body','text',default=''),
    Field('modified_on','datetime',default=timestamp),
    Field('modified_by',db.auth_user))

db.define_table('document',
    Field('page',db.page),
    Field('title'),
    Field('file','upload'),
    Field('uploaded_by',db.auth_user),
    Field('uploaded_on','datetime',default=timestamp))

db.document.page.requires=IS_IN_DB(db,'page.id','%(id)s:%(title)s')
db.document.title.requires=IS_NOT_EMPTY()
db.document.public_fields=['title','file']

db.define_table('comment',
    Field('page',db.page),
    Field('posted_on','datetime',default=timestamp),
    Field('author',db.auth_user),
    Field('disabled',default=False),
    Field('body','text',default=''))

db.comment.page.requires=IS_IN_DB(db,'page.id','%(id)s:%(title)s')
db.comment.body.requires=IS_NOT_EMPTY()
db.comment.public_fields=['body']
