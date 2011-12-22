
db.define_table('survey',
                Field('owner',db.auth_user),
                Field('timestamp','datetime',default=timestamp),
                Field('start','date',default=today),
                Field('stop','date',default=today+datetime.timedelta(7)),
                Field('title'),
                Field('description','text',default=''),
                Field('is_assignment','boolean',default=True),
                Field('normalize_score_to','double',default=100.0),
                Field('anonymous','boolean',default=False))

db.survey.title.requires=IS_NOT_EMPTY()
db.survey.access_types=['none','take']
db.survey.public_fields=['title','description','is_assignment','normalize_score_to','start','stop','anonymous']

db.define_table('sa',
                Field('survey',db.survey),
                Field('owner',db.auth_user),
                Field('anonymous','boolean',default=False),
                Field('timestamp','datetime',default=None),
                Field('score','double',default=0.0),
                Field('reviewer_comment','text',default=''),
                Field('completed','boolean'))

db.sa.survey.requires=IS_IN_DB(db,db.survey.id,db.survey.title)
db.sa.public_fields=['score','reviewer_comment']

db.define_table('question',
                Field('survey',db.survey),
                Field('number','integer'),
                Field('title','string'),
                Field('body','text',default=''),
                Field('type','string',default='short text'),
                Field('minimum','integer',default=0),
                Field('maximum','integer',default=5),
                Field('correct_answer'),
                Field('points','double',default=0),
                Field('option_A','string',default=''),
                Field('points_for_option_A','double',default=0),
                Field('option_B','string',default=''),
                Field('points_for_option_B','double',default=0),
                Field('option_C','string',default=''),
                Field('points_for_option_C','double',default=0),
                Field('option_D','string',default=''),
                Field('points_for_option_D','double',default=0),
                Field('option_E','string',default=''),
                Field('points_for_option_E','double',default=0),
                Field('option_F','string',default=''),
                Field('points_for_option_F','double',default=0),
                Field('option_G','string',default=''),
                Field('points_for_option_G','double',default=0),
                Field('option_H','string',default=''),
                Field('points_for_option_H','double',default=0),
                Field('required','boolean',default=True),
                Field('comments_enabled','boolean',default=False))

question_fields=[x for x in db.question.fields if not x in ['id','number','survey']]

db.question.survey.requires=IS_IN_DB(db,'survey.id','survey.title')
db.question.title.requires=IS_NOT_EMPTY()
db.question.type.requires=IS_IN_SET(['short text','long text','long text verbatim','integer','float','date','multiple exclusive','multiple not exclusive','upload'])
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
                Field('sa',db.sa),
                Field('value','string'),
                Field('file','upload'),
                Field('grade','double',default=None),
                Field('comment','text',default=''))

db.answer.question.requires=IS_IN_DB(db,db.question.id,db.question.title)
db.sa.requires=IS_IN_DB(db,db.sa.id,db.sa.id)

def mysurvey():
    if len(request.args)<0: redirect(URL(r=request,f='index'))
    surveys=db(db.survey.id==request.args[0])(db.survey.owner==session.person_id).select()
    if len(surveys)<1:
        session.flash='your are not authorized'
        redirect(URL(r=request,f='index'))
    return surveys[0]

def thissurvey():
    if len(request.args)<1: redirect(URL(r=request,f='index'))
    survey_id=request.args[0]
    if not has_access(person_id,'survey',survey_id,'take'):
        session.flash='access denied'
        redirect(URL(r=request,f='index'))
    rows=db(db.survey.id==survey_id).select()
    if not len(rows):
        session.flash='survey is missing'
        redirect(URL(r=request,f='index'))
    rows2=db(db.sa.owner==person_id)(db.sa.survey==survey_id).select()
    if not len(rows2):
       id=db.sa.insert(survey=survey_id,owner=person_id,completed=False,
                       anonymous=rows[0].anonymous)
       rows2=db(db.sa.id==id).select()
    return rows[0],rows2[0]
