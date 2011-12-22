# a table to store posted messages
db.define_table('post',
    Field('body','text',requires=IS_NOT_EMPTY(),label='What is on your mind?'),
    Field('posted_on','datetime',readable=False,writable=False),
    Field('posted_by','reference auth_user',readable=False,writable=False))

# a table to link two people
db.define_table('link',
    Field('source','reference auth_user'),
    Field('target','reference auth_user'),
    Field('accepted','boolean',default=False))

# and define some global variables that will make code more compact
User, Link, Post = db.auth_user, db.link, db.post
me, a0, a1 = auth.user_id, request.args(0), request.args(1)
myfriends = db(Link.source==me)(Link.accepted==True)
alphabetical = User.first_name|User.last_name
def name_of(user): return '%(first_name)s %(last_name)s' % user
