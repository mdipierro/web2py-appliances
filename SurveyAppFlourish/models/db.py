#########################################################################
# This scaffolding model makes your app work on Google App Engine too   #
#########################################################################

try:
    from gluon.contrib.gql import *         # if running on Google App Engine
except:
    db=DAL('sqlite://storage.db')         # if not, use SQLite or other DB
else:
    db=GQLDB()                              # connect to Google BigTable
    session.connect(request,response,db=db) # and store sessions there
#session.forget()                           # uncomment for no session at all

#########################################################################
# Define your tables below, for example                                 #
#                                                                       #
# >>> db.define_table('mytable',Field('myfield','string'))           #
#                                                                       #
# Fields can be 'string','text','password','integer','double','booelan' #
#       'date','time','datetime','blob','upload', 'reference TABLENAME' #
# There is an implicit 'id integer autoincrement' field                 #
# Consult manual for more options, validators, etc.                     #
#                                                                       #
# More API examples for controllers:                                    #
#                                                                       #
# >>> db.mytable.insert(myfield='value')                                #
# >>> rows=db(db.mytbale.myfield=='value).select(db.mytable.ALL)        #
# >>> for row in rows: print row.id, row.myfield                        #
#########################################################################

import datetime
now=datetime.datetime.now()

db.define_table('survey',
   db.Field('email'),
   db.Field('title',length=128),
   db.Field('code_edit',length=128),
   db.Field('code_take',length=128))

db.define_table('sa',
                Field('survey',db.survey),
                Field('session_id',length=128,default=response.session_id),
                Field('created_ip'),
                Field('modified_on','datetime',default=None),
                Field('completed','boolean'))

db.sa.survey.requires=IS_IN_DB(db,db.survey.id,'%(title)s by %(email)s')

db.define_table('question',
                Field('survey',db.survey),
                Field('number','integer'),
                Field('title','string'),
                Field('body','text',default=''),
                Field('type','string',default='short text'),
                Field('minimum','integer',default=0),
                Field('maximum','integer',default=5),
                Field('correct_answer'),
                Field('points','double',default=0.0),
                Field('option_A','string',length=4096,default=''),
                Field('points_for_option_A','double',default=0.0),
                Field('option_B','string',length=4096,default=''),
                Field('points_for_option_B','double',default=0.0),
                Field('option_C','string',length=4096,default=''),
                Field('points_for_option_C','double',default=0.0),
                Field('option_D','string',length=4096,default=''),
                Field('points_for_option_D','double',default=0.0),
                Field('option_E','string',length=4096,default=''),
                Field('points_for_option_E','double',default=0.0),
                Field('option_F','string',length=4096,default=''),
                Field('points_for_option_F','double',default=0.0),
                Field('option_G','string',length=4096,default=''),
                Field('points_for_option_G','double',default=0.0),
                Field('option_H','string',length=4096,default=''),
                Field('points_for_option_H','double',default=0.0),
                Field('required','boolean',length=4096,default=True),
                Field('comments_enabled','boolean',default=False))

question_fields=[x for x in db.question.fields if not x in ['id','number','survey']]

db.question.survey.requires=IS_IN_DB(db,'survey.id','%(title)s by %(email)s')
db.question.title.requires=IS_NOT_EMPTY()
db.question.type.requires=IS_IN_SET(['short text','long text','long text verbatim','integer','float','multiple exclusive','multiple not exclusive'])
db.question.points.requires=IS_FLOAT_IN_RANGE(0,100)
db.question.points_for_option_A.requires=IS_FLOAT_IN_RANGE(0,100)
db.question.points_for_option_B.requires=IS_FLOAT_IN_RANGE(0,100)
db.question.points_for_option_C.requires=IS_FLOAT_IN_RANGE(0,100)
db.question.points_for_option_D.requires=IS_FLOAT_IN_RANGE(0,100)
db.question.points_for_option_E.requires=IS_FLOAT_IN_RANGE(0,100)
db.question.points_for_option_F.requires=IS_FLOAT_IN_RANGE(0,100)
db.question.points_for_option_G.requires=IS_FLOAT_IN_RANGE(0,100)
db.question.points_for_option_H.requires=IS_FLOAT_IN_RANGE(0,100)

db.define_table('answer',
                Field('question',db.question),
                Field('survey',db.survey),
                Field('sa',db.sa),
                Field('value','blob'),
                Field('file','upload'),
                Field('grade','double',default=None),
                Field('comment','text',default=''))

db.answer.question.requires=IS_IN_DB(db,db.question.id,db.question.title)
db.sa.requires=IS_IN_DB(db,db.sa.id,db.sa.id)
