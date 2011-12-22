import cPickle, re, shutil, os
from gluon.storage import Storage

@auth.requires_login()
def index():
    surveys_owned=accessible('survey',('take',))\
         ((db.survey.stop>=today)|(db.survey.owner==auth.user_id))\
         (db.auth_user.id==db.survey.owner)\
         .select(orderby=~db.survey.stop|db.survey.id)
    surveys_todo=accessible('survey',('take',))\
         ((db.survey.stop>=today)|(db.survey.owner==auth.user_id))\
         (db.auth_user.id==db.survey.owner)\
         (~db.survey.id.belongs(db(db.sa.owner==auth.user_id)\
               (db.sa.completed==True)._select(db.sa.survey)))\
         .select(orderby=~db.survey.stop|db.survey.id)
    surveys_done=accessible('survey',('take',))\
         ((db.survey.stop>=today)|(db.survey.owner==auth.user_id))\
         (db.auth_user.id==db.survey.owner)\
         (db.sa.owner==auth.user_id)\
         (db.sa.survey==db.survey.id)\
         (db.sa.completed==True)\
         .select(orderby=~db.survey.stop|db.survey.id)
    return dict(surveys_owned=find_groups(surveys_owned),\
                surveys_todo=find_groups(surveys_todo),\
                surveys_done=find_groups(surveys_done))

@auth.requires_login()
def create_survey():
    form=SQLFORM(db.survey,fields=db.survey.public_fields)
    form.vars.owner=auth.user_id
    if form.accepts(request,session):
        db.access.insert(table_name='survey',record_id=form.vars.id,\
                         persons_group=g_tuple[1],access_type="take")
        db.sa.insert(survey=form.vars.id,owner=auth.user_id)
        session.flash='suryvey created'
        redirect(URL('edit_questions',args=[form.vars.id]))
    return dict(form=form)

@auth.requires_login()
def edit_survey():
    survey=mysurvey()
    form=SQLFORM(db.survey,survey,\
         fields=db.survey.public_fields,deletable=True,showid=False)
    form.vars.owner=auth.user_id
    if form.accepts(request,session):
        session.flash='survey updated'
        redirect(URL('edit_questions',args=request.args))
    return dict(form=form)

@auth.requires_login()
def link_survey():
    survey=mysurvey()
    return dict(survey=survey,host=HOST)

@auth.requires_login()
def edit_questions():
    survey=mysurvey()
    if len(request.args)>1: question_id=request.args[1]
    else: question_id=0
    rows=db(db.question.survey==survey.id)\
           (db.survey.id==survey.id)\
           (db.survey.owner==auth.user_id).select(orderby=db.question.number)
    if len(rows) and question_id==0: question_id=rows[0].question.id
    form=''
    if question_id>0:
        qrows=db(db.question.id==question_id)\
                (db.question.survey==db.survey.id)\
                (db.survey.owner==auth.user_id).select()
        if len(qrows):
            form=SQLFORM(db.question,qrows[0].question,showid=False,
                 fields=question_fields,deletable=db.survey.owner==auth.user_id)
            if form.accepts(request,session):
                session.flash='quesiton modified'
                redirect(URL(r=request,args=request.args))
            elif form.errors:
                response.flash='there is an error in the form'
    return dict(rows=rows,survey=survey,form=form,question_id=question_id)

@auth.requires_login()
def append_question():
    survey=mysurvey()
    rows=db(db.question.survey==survey.id).select(orderby=~db.question.number,\
                                                  limitby=(0,1))
    if rows: number=rows[0].number+1
    else: number=1
    i=db.question.insert(title='New Question',\
                         number=number,body='',survey=survey.id)
    args=[survey.id,i]
    redirect(URL('edit_questions',args=args))

@auth.requires_login()
def take_survey():
    survey,sa=thissurvey()
    questions=db(db.question.survey==survey.id).select(orderby=db.question.number)
    if not len(questions):
        session.flash='doh! there are no questions in this survey'
        redirect(URL('index',args=request.args[:1]))
    question=questions[0]
    if len(request.args)>1: question_id=request.args[1]
    else: question_id=0
    if question_id>0:
        for item in questions:
            if str(item.id)==question_id: question=item
    requires=[]
    answers=db(db.answer.sa==sa.id)(db.answer.question==question.id).select()
    if len(answers):
        answer_value=cPickle.loads(answers[0].value)
        answer_comment=answers[0].comment
        answer_id=answers[0].id
        answer_file=answers[0].file
    else:
        answer_value=''
        answer_comment=''
        answer_id=db.answer.insert(sa=sa.id,question=question.id,\
                                   value=cPickle.dumps(answer_value))
        answer_file=None
    if question.required: requires.append(IS_NOT_EMPTY())
    if question.type=='short text':
        stuff=INPUT(_name='value',value=answer_value,requires=requires)
    elif question.type=='long text':
        stuff=TEXTAREA(_name='value',value=answer_value,requires=requires,_id='answer_long_text')
    elif question.type=='long text verbatim':
        stuff=TEXTAREA(_name='value',value=answer_value,requires=requires,_class='verbatim')
    elif question.type=='integer':
        try: answer_value=int(answer_value)
        except: answer_value=''
        requires.append(IS_INT_IN_RANGE(question.minimum,question.maximum))
        stuff=INPUT(_name='value',value=answer_value,requires=requires,_class='integer')
    elif question.type=='float':
        try: answer_value=float(answer_value)
        except: answer_value=''
        requires.append(IS_FLOAT_IN_RANGE(question.minimum,question.maximum))
        stuff=INPUT(_name='value',value=answer_value,requires=requires,_class='double')
    elif question.type=='date':
        if IS_DATE()(str(answer_value))[1]: answer_value=''
        if question.required: requires=IS_NULL_OR(IS_DATE())
        else: requires=IS_DATE()
        stuff=INPUT(_name='value',value=answer_value,requires=requires,_class='date')
    elif question.type=='upload':
        if question.required: requires=IS_NOT_EMPTY()
        upload=URL('download_attachment',args=[sa.id])
        stuff=INPUT(_type='file',_name='file', requires=requires)
        if answer_file:
            stuff=DIV(stuff,'[',A('file',_href=upload+'/'+answer_file),'|',\
                      INPUT(_type='checkbox',_name='file__delete'),'delete]')
    else:
        options=[question['option_'+c] for c in ['A','B','C','D','E','F','G','H'] if question['option_'+c].strip()]
    if question.type=='multiple exclusive':
        stuff=TABLE(*[TR(INPUT(_type="radio",_name="value",_value=str(i),\
              value=answer_value),item) for i,item in enumerate(options)])
    elif question.type=='multiple not exclusive':
        items=[]
        for i,item in enumerate(options):
            if isinstance(answer_value,list) and str(i) in answer_value:
                items.append(TR(INPUT(_type="checkbox",_name="value",_value=i,\
                                      _checked=ON),item))
            else:
                items.append(TR(INPUT(_type="checkbox",_name="value",_value=i),item))
        stuff=TABLE(*[TR(item) for item in items])
    elif question.type=='multiple sortable':
        session.order_question=range(len(options))
        stuff=UL(*[LI(item,_class=i) for i,item in enumerate(options)])
    if question.comments_enabled:
        form=FORM(H2('Your answer'),stuff,BR(),BR(),A('add a comment',_onclick="$('#comment_slide').slideToggle();"),
                  DIV(TEXTAREA(_name='comment',value=answer_comment,_id='answer_comment'),_id='comment_slide'),BR(),BR(),
                  INPUT(_type='image',_src=URL(r=request,c='static',f='surveys/submit.png')))
    else:
        form=FORM(H2('Your answer'),stuff,BR(),BR(),
                  INPUT(_type='image',_src=URL(r=request,c='static',f='surveys/submit.png')))
    if form.accepts(request,session):
        if not form.vars.value and question.type[:8]=='multiple' and \
           question.required:
            response.flash='an answer is required'
            return dict(questions=questions,survey=survey,
                        form=form,question=question)
        if question.type=='upload':
            if request.vars.file__delete=='on':
                 filename=''
            elif request.vars.file!=None and not isinstance(request.vars.file,(str,unicode)):
                 try: ext=re.compile('\.\w+$').search(request.vars.file.filename.lower()).group()
                 except: ext='.txt'
                 filename='answer.file.%s.%s'%(str(random.random())[2:],ext)
                 pathfilename=os.path.join(request.folder,'uploads',filename)
                 dest_file=open(pathfilename,'wb')
                 shutil.copyfileobj(request.vars.file.file,dest_file)
                 dest_file.close()
            else: filename=None
            if filename!=None:
                 db(db.answer.id==answer_id).update(file=filename,comment=form.vars.comment)
            else:
                 db(db.answer.id==answer_id).update(comment=form.vars.comment)
        else:
            db(db.answer.id==answer_id)\
                .update(value=cPickle.dumps(form.vars.value),\
                comment=form.vars.comment)
        session.flash='answer recorded'
        redirect(URL(r=request,args=request.args))
    elif form.errors:
        response.flash='invalid value'
    return dict(questions=questions,survey=survey,form=form,question=question)

@auth.requires_login()
def done_survey():
    survey,sa=thissurvey()
    sa.update_record(completed=True,timestamp=timestamp)
    session.flash='survey completed, thank you'
    redirect(URL('index'))

@auth.requires_login()
def match(a,b):
    return str(a).strip()==str(b).strip()

@auth.requires_login()
def report():
    survey=mysurvey()
    if len(request.args)<2:
       sas=db(db.sa.survey==survey.id)\
             (db.sa.owner==db.auth_user.id).select(orderby=db.auth_user.name)
       rows=db(db.question.survey==survey.id)\
              (db.answer.question==db.question.id)\
              (db.answer.sa==db.sa.id)\
              (db.auth_user.id==db.sa.owner).select(orderby=db.question.id|db.auth_user.name)
    else:
       sas=db(db.sa.owner==request.args[1])\
             (db.sa.survey==survey.id)\
             (db.sa.owner==db.auth_user.id).select(orderby=db.auth_user.name)
       rows=db(db.question.survey==survey.id)\
              (db.answer.question==db.question.id)\
              (db.answer.sa==db.sa.id)\
              (db.auth_user.id==db.sa.owner)\
              (db.auth_user.id==request.args[1]).select(orderby=db.question.id|db.auth_user.name)
    total_points={}
    points={}
    for r in sas:
        total_points[r.auth_user.id]=0.0
        points[r.auth_user.id]={}
        for row in rows:
            if row.auth_user.id==r.auth_user.id:
               points[r.auth_user.id][row.question.id]=p=0.0
               if row.question.type in ['short text','integer','float','date']\
                  and row.question.correct_answer \
                  and match(cPickle.loads(row.answer.value),\
                            row.question.correct_answer):
                   p=row.question.points
               elif row.question.type[:8]=='multiple':
                   p=0.0
                   for item in cPickle.loads(row.answer.value):
                       p+=row.question['points_for_option_%s' % chr(ord('A')+int(item))]
               points[r.auth_user.id][row.question.id]=p
               total_points[r.auth_user.id]+=p
    return dict(rows=rows,survey=survey,sas=sas,total_points=total_points,points=points)

@auth.requires_login()
def aggregate(items):
   d={}
   for item in items:
       try:
           d[item]+=1
       except:
           d[item]=1
           pass
       pass
   return [[c,v] for c,v in d.items()]

@auth.requires_login()
def stats():
    import cPickle
    r=report()
    survey=r['survey']
    rows=r['rows']
    d=[]
    question_id=0
    ltype=0
    n=len(db(db.sa.survey==survey.id).select(db.sa.id))
    for row in rows:
        if row.question.type in ['short text','long text','date']: continue
        if not question_id: question_id,values=row.question.id,[]
        elif question_id!=row.question.id and ltype:
             question_id,lid=row.question.id,question_id
             values=aggregate(values)
             d.append([lid,lquestion,values,ltype])
             values=[]
        if row.question.type in ['short text','long text','date']: continue
        value=cPickle.loads(row.answer.value)
        try:
           if row.question.type in ['integer','float']: ivalue=[int(value)]
           if row.question.type[:8]=='multiple': ivalue=[int(x) for x in value]
        except: ivalue=[]
        values+=ivalue
        ltype,lquestion=row.question.type,row.question.title
    if ltype:
        values=aggregate(values)
        d.append([question_id,row.question.title,values,ltype])
    return dict(rows=d, survey=survey,n=n)

@auth.requires_login()
def delete_sa():
    if len(request.args)<2: redirect(URL('index'))
    survey=mysurvey()
    if int(request.args[1])!=auth.user_id:
        db(db.sa.owner==request.args[1])(db.sa.survey==survey.id).delete()
    redirect(URL('report',args=[survey.id]))

@auth.requires_login()
def save():
    survey=mysurvey()
    fields=['question.'+x for x in db.question.fields if not x in ['id','survey']]
    questions=db(db.question.survey==survey.id).select(*fields)
    data=dict(
      version=1.0,
      title=survey.title,
      description=survey.description,
      start=survey.start,
      stop=survey.stop,
      anonymous=survey.anonymous,
      questions_colnames=questions.colnames,
      questions_response=questions.response
    )
    pickled_data=cPickle.dumps(data)
    response.headers['Content-Type']='application/pickle'
    return pickled_data

@auth.requires_login()
def upload_survey():
    if request.vars.file==None or not hasattr(request.vars.file,'file'):
        return dict()
    try:
        data=Storage(cPickle.loads(request.vars.file.file.read()))
        if data.version!=1.0: response.flash='incompatible version'
    except:
        session.flash='unable to read file'
    try:
        i=db.survey.insert(title=data.title,\
                           description=data.description,
                           start=data.start,stop=data.stop,
                           anonymous=data.anonymous,
                           owner=auth.user_id)
        db.access.insert(table_name='survey',record_id=i,\
                         persons_group=g_tuple[1],access_type="take")
        db.sa.insert(survey=i,owner=auth.user_id)
    except:
        session.flash='file is in wrong format'
    try:
        for item in data.questions_response:
            d={'survey':i}
            for j,c in enumerate(data.questions_colnames): d[c[9:]]=item[j]
            db.question.insert(**d)
            session.flash='new survey (%i) uploaded' % i
            redirect(URL('edit_survey',args=[i]))
    except Exception:
        session.flash='unable to unpack questions from file'
    redirect(URL('index'))

@auth.requires_login()
def sort_questions():
    survey=mysurvey()
    for i,item in enumerate(request.vars.order.split(',')[:-1]):
        db(db.question.id==item)(db.question.survey==survey.id).update(number=i)
    return 'done'

### complete the following

@auth.requires_login()
def download_attachment(): return ''

### show report to students

### gradebook
