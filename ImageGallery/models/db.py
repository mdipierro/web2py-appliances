# try something like
db=DAL("sqlite://db.db")

db.define_table('show',
  Field('name'))

db.define_table('image',
  Field('show',db.show),
  Field('title'),
  Field('file','upload'))


db.show.name.requires=[IS_NOT_EMPTY(),IS_NOT_IN_DB(db,db.show.name)]
db.image.show.requires=IS_IN_DB(db,db.show.id,'%(name)s')
