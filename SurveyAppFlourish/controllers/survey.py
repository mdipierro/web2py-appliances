import cPickle, re, shutil, os, uuid


response.title=settings.title
if request.function=='index':
    response.subtitle=settings.subtitle
else:
    response.subtitle='powered by '+settings.title

response.menu=[
   ['Home',request.function=='index',URL('index')],
]

def index():
    form=FORM(TABLE(TR('Survey title: ',INPUT(_name='title',requires=IS_NOT_EMPTY())),
                    TR('Your email: ',INPUT(_name='email',requires=IS_EMAIL())),
                    TR('',INPUT(_type='submit'))))
    if form.accepts(request,session):
        code_edit=str(uuid.uuid4())
        code_take=str(uuid.uuid4())
        db.survey.insert(email=form.vars.email,title=form.vars.title,
                         code_edit=code_edit,code_take=code_take)
        message="""
Welcome to %(title)s

An empty survey has been create for you.
You can edit the survey at %(host)s/%(app)s/survey/edit/%(code_edit)s
People can take the survey at %(host)s/%(app)s/survey/take/%(code_take)s
""" % dict(title=response.title,host=settings.host_url,app=request.application,code_edit=code_edit,code_take=code_take)
        if email(sender=settings.email_sender,to=form.vars.email,subject=response.title,
                 message=message,server=settings.email_server,auth=settings.email_auth):
            response.flash=T('We sent you an email to active/edit the survey')
        else:
            response.flash=T('Sorry, we are unable to send you an email')
    return dict(form=form)

def __edit_survey():
    surveys=db(db.survey.code_edit==request.args[0]).select()
    if not surveys:
        session.flash='survey not found'
        redirect(URL('index'))
    return surveys[0]

def __take_survey():
    surveys=db(db.survey.code_take==request.args[0]).select()
    if not surveys:
        session.flash='survey not found'
        redirect(URL('index'))
    return surveys[0]

def edit():
    survey=__edit_survey()
    response.title=survey.title
    response.menu+=[
       [T('edit survey'),True,URL('edit',args=[survey.code_edit])],
       [T('take survey'),0,URL('take',args=[survey.code_take])],
       [T('results'),0,URL('results',args=[survey.code_edit])],
    ]
    rows=db(db.question.survey==survey.id).select()
    rows=sorted(rows,lambda x,y: +1 if y.number<x.number else -1)
    rows_count=len(rows)
    if not rows_count or request.vars.new:
       rows_count=max([-1]+[row.number for row in rows])+1
       question_id=db.question.insert(survey=survey.id,
         title='question #%i'%(rows_count+1),number=rows_count)
       redirect(URL(r=request,args=[request.args[0],question_id]))
    question_id=0
    if len(request.args)>1: question_id=request.args[1]
    if question_id==0: question_id=rows[0].id
    form=''
    if question_id>0:
        qrows=db(db.question.id==question_id).select()
        if not qrows or qrows[0].survey!=survey.id: redirect(r=request,f='index')
        if len(qrows):
            form=SQLFORM(db.question,qrows[0],showid=False,
                         fields=question_fields,deletable=True)
            if form.accepts(request,session):
                if request.vars.delete_this_record:
                    session.flash='question deleted'
                    redirect(URL(r=request,args=request.args[:1]))
                session.flash='quesiton modified'
                redirect(URL(r=request,args=request.args))
            elif form.errors:
                response.flash='there is an error in the form'
    return dict(rows=rows,survey=survey,form=form,question_id=question_id)

def take():
    survey=__take_survey()
    response.title=survey.title
    sas=db(db.sa.session_id==response.session_id)(db.sa.survey==survey.id).select()
    if not sas:
        db.sa.insert(session_id=response.session_id,survey=survey.id,created_ip=request.client)
        sas=db(db.sa.session_id==response.session_id).select()
    sa=sas[0]
    if sa.completed:
        response.flash=T('you have already completed this survey')
    rows=db(db.question.survey==survey.id).select()
    questions=sorted(rows,lambda x,y: +1 if y.number<x.number else -1)
    if not len(questions):
        session.flash=T('this survey does not contain questions yet')
        redirect(URL('index'))
    question=questions[0]
    if len(request.args)>1: question_id=request.args[1]
    else: question_id=0
    j,next=None,None
    if question_id==0 and len(questions)>1: next=questions[1].id
    if question_id>0:
        for k,item in enumerate(questions):
            if str(item.id)==question_id: j,question=k+1,item
            if k==j: next=item.id
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
        answer_id=db.answer.insert(survey=survey.id,
                                   sa=sa.id,question=question.id,\
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
            if answer_value==str(i) or \
               (isinstance(answer_value,list) and str(i) in answer_value):
                items.append(TR(INPUT(_type="checkbox",_name="value",_value=str(i),\
                                      value=True),item))
            else:
                items.append(TR(INPUT(_type="checkbox",_name="value",_value=str(i),
                                      value=False),item))
        stuff=TABLE(*[TR(item) for item in items])
    elif question.type=='multiple sortable':
        session.order_question=range(len(options))
        stuff=UL(*[LI(item,_class=i) for i,item in enumerate(options)])
    if question.comments_enabled:
        form=FORM(H2('Your answer'),stuff,BR(),BR(),A('add a comment',_onclick="$('#comment_slide').slideToggle();"),
                  DIV(TEXTAREA(_name='comment',value=answer_comment,_id='answer_comment'),_id='comment_slide'),BR(),BR(),
                  INPUT(_type='image',_src=URL(r=request,c='static',f='submit.png')))
    else:
        form=FORM(H2('Your answer'),stuff,BR(),BR(),
                  INPUT(_type='image',_src=URL(r=request,c='static',f='submit.png')))
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
        db(db.sa.session_id==response.session_id).update(modified_on=now)
        session.flash=T('answer recorded')
        if next: redirect(URL(r=request,args=[request.args[0],next]))
        else: redirect(URL('done',args=request.args[:1]))
    elif form.errors:
        response.flash='invalid value'
    return dict(questions=questions,survey=survey,form=form,question=question)

def done():
    survey=__take_survey()
    response.title=survey.title
    db(db.sa.session_id==response.session_id).update(completed=True,modified_on=now)
    return dict()

def match(a,b):
    return str(a).strip()==str(b).strip()

def aggregate(items):
   d={}
   for item in items:
       try:
           d[item]+=1
       except:
           d[item]=1
           pass
       pass
   return [[c,'#4E7DD1',v] for c,v in d.items()]

def results():
    import cPickle, re
    def normalize(text): return re.sub('\s+',' ',text.strip()).lower()
    survey=__edit_survey()
    response.menu+=[
       [T('edit survey'),0,URL('edit',args=[survey.code_edit])],
       [T('take survey'),0,URL('take',args=[survey.code_take])],
       [T('results'),True,URL('results',args=[survey.code_edit])],
    ]
    response.title=survey.title
    sas=db(db.sa.survey==survey.id).select()
    previous,d,qk,values=None,[],{},[]
    questions=db(db.question.survey==survey.id).select()
    for q in questions: qk[q.id]=q
    answers=db(db.answer.survey==survey.id).select()
    answers=[a for a in answers if qk.has_key(a.question)]
    answers=sorted(answers,lambda x,y: +1 if qk[y.question].number<qk[x.question].number else -1)
    for answer in answers:
        value=cPickle.loads(answer.value)
        if value=='': continue
        question=qk[answer.question]
        if question.type in ['date','long text','long text verbatim']: continue
        if previous and previous.id!=question.id:
             d.append([previous,aggregate(values)])
             values=[]
        if question.type=='integer': ivalue=[int(value)]
        elif question.type=='float': ivalue=[float(value)]
        elif question.type[:8]=='multiple':
            value=re.compile('\d+').findall(str(value))
            ivalue=[chr(ord('A')+int(x)) for x in value]
        else: ivalue=[normalize(str(value))]
        values+=ivalue
        previous=question
    if previous: d.append([previous,aggregate(values)])
    return dict(rows=d,survey=survey,sas=sas)

def answer():
    import cPickle
    survey=__edit_survey()
    response.menu+=[
       [T('edit survey'),0,URL('edit',args=[survey.code_edit])],
       [T('take survey'),0,URL('take',args=[survey.code_take])],
       [T('results'),0,URL('results',args=[survey.code_edit])],
    ]
    response.title=survey.title
    if not len(request.args)==2: redirect(URL('index'))
    qk={}
    questions=db(db.question.survey==survey.id).select()
    for q in questions: qk[q.id]=q
    sas=db(db.sa.id==request.args[1]).select()
    if not sas: redirect(URL('index'))
    else: sa=sas[0]
    answers=db(db.answer.survey==survey.id)(db.answer.sa==sa.id).select()
    answers=[a for a in answers if qk.has_key(a.question)]
    answers=sorted(answers,lambda x,y: +1 if qk[y.question].number<qk[x.question].number else -1)
    answers=[(qk[a.question],cPickle.loads(a.value),a.comment) for a in answers]
    return dict(survey=survey,sa=sa,answers=answers)

def sort_questions():
    survey=__edit_survey()
    for i,item in enumerate(request.vars.order.split(',')[:-1]):
        items=db(db.question.id==item).select()
        if items and items[0].survey==survey.id: items[0].update_record(number=i)
    return 'done'
