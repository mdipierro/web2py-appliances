# coding: utf8
import datetime
RELATIONS = (SELF,MOTHER,FATHER,SIBLING,RELATIVE,FRIEND)=('self','mother','father','sibling','relative','friend')

is_phone=IS_MATCH('\+?[\d\-\#]+',error_message="Example: +39-111-1234#1234")

db.define_table('contact',
                Field('patient',db.auth_user,writable=False),
                Field('full_name'),
                Field('active_since','date',default=request.now),
                Field('active_until','date',default=request.now+datetime.timedelta(days=3652)),
                Field('relation',requires=IS_IN_SET(RELATIONS)),
                Field('home_hone',requires=is_phone),
                Field('cell_hone',requires=is_phone),
                Field('address'),
                Field('zip_code'),
                Field('state'),
                Field('country',requires=IS_IN_SET(COUNTRIES)),
                Field('info','text'),
                format='%(name)s')

db.define_table('insuarance',
                Field('patient',db.auth_user,writable=False),
                Field('full_name'),
                Field('active_since','date',default=request.now),
                Field('active_until','date',default=request.now+datetime.timedelta(days=365)),
                Field('insurance_name'),
                Field('plan_type'),
                Field('plan_code'),
                Field('insured_code'),
                Field('info','text'),
                format='$(insurance_name)s')

CATEGORIES = (FACT, ASSUMPTION, ACTION) = ('fact','assumption', 'action')
IMPORTANCE = (HIGH, MEDIUM, LOW) = ('high', 'medium', 'low')
PROBABILITY = (HIGH, MEDIUM, LOW)

db.define_table('post',
                Field('patient',db.auth_user,writable=False),
                Field('category',requires=IS_IN_SET(CATEGORIES,zero=None)),
                Field('title',requires=IS_NOT_IN_DB(db,'post.title')),
                Field('comment','text'),
                Field('importance',requires=IS_IN_SET(IMPORTANCE,zero=None)),
                Field('probability',requires=IS_IN_SET(PROBABILITY,zero=None)),
                Field('posted_on','datetime',default=request.now,readable=False,writable=False),
                Field('posted_by',db.auth_user,default=auth.user_id,readable=False,writable=False),
                Field('expired','boolean',default=False,readable=False,writable=False),
                Field('expires_on','datetime',default=request.now,readable=False,writable=False),
                Field('expired_by',db.auth_user,default=auth.user_id,readable=False,writable=False),
                Field('reasons'),
                format='%(posted_on)s %(title)s')

db.auth_user.id.represent=lambda id: A('go',_href=URL(r=request,c='default',f='backlog',args=id))

#from gluon.contrib.populate import *
#populate(db.auth_user,100)
#populate(db.post,300)

def trusted_by(patient):
    import re
    regex = re.compile('\d+')
    net = regex.findall(patient.trusted_doctors)
    for doctor_id in re.compile('\d+').findall(patient.trusted_doctors):
        doctor=db.auth_user[doctor_id]
        if doctor.doctor:
            net+=regex.findall(doctor.trusted_others)
    if settings.enforce_permissions:
        if patient.patient and not str(auth.user.id) in patient.trusted_doctors:
            session.flash='Not authorized'
            redirect(URL(r=request,f='index'))
