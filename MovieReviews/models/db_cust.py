db.define_table('format',
                Field('created_by', db.auth_user, default=auth.user_id),
                Field('modified_by', db.auth_user, default=auth.user_id),
                Field('name'),format='%(name)s')
db.define_table('country',
                Field('created_by', db.auth_user, default=auth.user_id),
                Field('modified_by', db.auth_user, default=auth.user_id),
                Field('name'),format='%(name)s')
db.define_table('category',
                Field('created_by', db.auth_user, default=auth.user_id),
                Field('modified_by', db.auth_user, default=auth.user_id),
                Field('name'),format='%(name)s')
db.define_table('movie',
                Field('name'),
                Field('director'),
                Field('category', db.category),
                Field('country', db.country),
                Field('format', db.format),
                Field('description', 'text'),
                Field('Review', 'text'),
                Field('created_by', db.auth_user, default=auth.user_id),
                Field('modified_by', db.auth_user, default=auth.user_id),)
db.define_table('review',
               Field('author',db.auth_user,default=auth.user_id,writable=False,readable=False),
               Field('movie',db.movie,writable=False,readable=False),
               Field('body','text'),
               Field('created_by', db.auth_user, default=auth.user_id),
               Field('modified_by', db.auth_user, default=auth.user_id),)


db.movie.name.requires=IS_NOT_EMPTY()
