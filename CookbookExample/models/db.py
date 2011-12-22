import datetime; now=datetime.date.today()
db=DAL('sqlite://db.db')

db.define_table('category',Field('name'))

db.define_table('recipe',
                Field('title'),
                Field('description',length=256),
                Field('category',db.category),
                Field('date','date',default=now),
                Field('instructions','text'))

db.category.name.requires=[IS_NOT_EMPTY(),IS_NOT_IN_DB(db,'category.name')]
db.recipe.title.requires=[IS_NOT_EMPTY()]
db.recipe.description.requires=IS_NOT_EMPTY()
db.recipe.category.requires=IS_IN_DB(db,'category.id','category.name')
db.recipe.date.requires=IS_DATE()