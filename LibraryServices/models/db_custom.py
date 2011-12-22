db.define_table('book',
                Field('authors',requires=IS_NOT_EMPTY()),
                Field('title',requires=IS_NOT_EMPTY()),
                Field('publisher'),
                Field('publication_year','integer'),
                Field('isbn13',length=13),
                Field('isbn10',length=10),
                Field('description','text'),
                Field('location'),
                format = '%(title)s')

db.define_table('loan',
                Field('book',db.book),
                Field('auth_user',db.auth_user),
                Field('loan_start','datetime'),
                Field('loan_end','datetime'))

