# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    return dict(message=T('Hello World'))

@auth.requires_login()
def manage():
    if request.args(1)=='new': db.quiz.code.readable=False
    else:
        db.quiz.code.represent = \
            lambda code,row:A('take',_href=URL('take',args=code))
    constraints = {'quiz':db.quiz.owner==auth.user.id}
    return dict(form = SQLFORM.smartgrid(db.quiz,constraints=constraints))
                                         

import re
class Grader:

    re_radio = re.compile('(?P<name>.*?):(?P<value>.*?):(?P<grade>\d+)')
    def __init__(self,request):
        import random, math
        self.request=request
        self.grade=0
        self.env = {'random':random,'math':math}

    def radio(self,text):
        try:
            m = self.re_radio.match(text)
            name = m.group('name')
            _value = m.group('value')
            value = self.request.vars.get(name,None)
            grade = int(m.group('grade')) 
        except Exception, e:
            return DIV(str(e),_class='error').xml()
        if grade and value==_value:
            self.grade += grade        
        if not self.request.vars:
            return INPUT(_type='radio',_name=name,_value=_value).xml()
        elif value==_value:
            if grade:
                return SPAN(INPUT(_type='radio',_checked=True,_disabled=True),
                            ' (%s points)' % grade,_style='color:green').xml()
            else:
                return SPAN(INPUT(_type='radio',_checked=True,_disabled=True),
                            ' (%s points)' % grade,_style='color:red').xml()
        else:
            return SPAN(INPUT(_type='radio',_checked=None,
                              _disabled=True),' (%s points)' % grade).xml()

    def checkbox(self,text):
        try:
            m = self.re_radio.match(text)
            name = m.group('name')
            _value = m.group('value')
            value = self.request.vars.get(name,None)
            if not isinstance(value,(list,tuple)): value = [value]
            grade = int(m.group('grade'))
        except Exception, e:
            return DIV(str(e),_class='error').xml()
        if grade and _value in value:
            self.grade += grade
        if not self.request.vars:
            return INPUT(_type='checkbox',_name=name,_value=_value).xml()
        elif _value in value:
            if grade:
                return SPAN(INPUT(_type='checkbox',_checked=True,_disabled=True),
                            ' (%s points)' % grade,_style='color:green').xml()
            else:
                return SPAN(INPUT(_type='checkbox',_checked=True,_disabled=True),
                            ' (%s points)' % grade,_style='color:red').xml()
        else:
            return SPAN(INPUT(_type='checkbox',_checked=None,
                              _disabled=True),' (%s points)' % grade).xml()
        
    def input(self,text):
        try:
            m = self.re_radio.match(text % self.env)
            name = m.group('name')
            _value = m.group('value')
            value = re.sub('\s+',' ',
                           self.request.vars.get(name,'').strip().lower())
            grade = int(m.group('grade'))
        except Exception, e:
            return DIV(str(e),_class='error').xml()
        try:
            if grade and 0.95*float(_value) < float(value) < 1.05*float(_value):
                self.grade += grade
            else:
                grade = 0
        except (TypeError,ValueError):
            if grade and _value==value:
                self.grade += grade
            else:
                grade = 0
        if not self.request.vars:
            return INPUT(_type='input',_name=name).xml()
        elif grade==0:
            return SPAN(INPUT(value=value,_disabled=True),
                        ' (should be %s)' % _value,
                        _style='color:red').xml()
        else:
            return SPAN(INPUT(value=value,_disabled=True),
                        ' (correct %s, points)' % grade,
                        _style='color:green').xml()

    def execute(self,text):
        try:
            if not self.env.get('_saved',False):
                exec(text,{},self.env)
        except Exception, e:
            return DIV(str(e),_class='error').xml()
        return ''
    
    def evaluate(self,text):
        try:
            return str(eval(text,{},self.env))
        except Exception, e:
            return DIV(str(e),_class='error').xml()

    def form(self,body):
        if session.env:
            for key,value in session.env.items():
                self.env[key] = value
        body+='\n'
        form = FORM(XML(MARKMIN(body,extra={'radio':self.radio,
                                            'check':self.checkbox,
                                            'input':self.input}).xml()))
        form.process()
        session.env = {'_saved':True}
        for key, value in self.env.items():
            if isinstance(value,(str,int,list,tuple,dict)):
                session.env[key] = value
            
        if not self.request.vars:
            form.append(INPUT(_type="submit"))
            form.grade=None
        else:
            response.flash = 'Your grade was recorded'
            message ='Your grade is %s. Print this page for your reference!' % self.grade
            form.insert(0,H2(message))
            form.grade=self.grade
        return form

TEST = """

# test1

## problem 1

``a=random.randint(5,10);b=random.randint(0,10)``:exec
``a``:eval + ``b``:eval = ?

- ``p:a:5``:radio ``a+b``:eval
- ``p:b:0``:radio ``a+b+1``:eval
- ``p:c:0``:radio ``a+b+2``:eval

## problem 2

- ``q:a:1``:check option 1
- ``q:b:2``:check option 2
- ``q:c:3``:check option 3

## problem 3

``t:456:1``:input type 456

"""

def test():
    return dict(form = Grader(request).form(TEST))

def make_quiz(body):
    return 'test'

@auth.requires_login()
def take():
    #db(db.report).delete()
    quiz = db.quiz(code=request.args(0)) or redirect(URL('index'))
    if quiz.time_restricted and not request.post_vars \
            and quiz.start_time and quiz.stop_time \
            and quiz.start_time<=request.now<=quiz.stop_time:
        session.flash="Time expired"
        redirect(URL('index'))
    report = db.report(student=auth.user.id,quiz=quiz.id)    
    while not report:
        session.env = None
        db.report.insert(student=auth.user.id,
                         quiz=quiz.id,
                         grade=None,
                         start_time=request.now)
        report = db.report(student=auth.user.id,quiz=quiz.id)
    if report.grade and not quiz.retake:
        session.flash = 'You have already taken this quiz (%s points)' % report.grade
        redirect(URL('index'))
    form = Grader(request).form(quiz.body)
    if form.grade!=None:
        report.update_record(grade=form.grade,
                             form=form.xml(),
                             answers=repr(dict(request.vars)),
                             stop_time=request.now)
    return dict(quiz=quiz,form=form,grade=form.grade)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
