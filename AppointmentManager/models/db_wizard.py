### we prepend t_ to tablenames and f_ to fieldnames for disambiguity


########################################
db.define_table('t_appointment',
    Field('id','id',
          represent=lambda id:SPAN(id,' ',A('view',_href=URL('appointment_read',args=id)))),
    Field('f_title', type='string', notnull=True,
          label=T('Title')),
    Field('f_start_time', type='datetime',
          label=T('Start Time')),
    Field('f_end_time', type='datetime',
          label=T('End Time')),
    Field('f_location', type='string',
          label=T('Location')),
    Field('f_latitude', type='double',
          writable=False,
          label=T('Latitude')),
    Field('f_longitude', type='double',
          writable=False,
          label=T('Longitude')),
    Field('f_log', type='text',
          represent=lambda x: MARKMIN(x),
          comment='WIKI (markmin)',
          label=T('Log')),
    Field('active','boolean',default=True,
          label=T('Active'),writable=False,readable=False),
    Field('created_on','datetime',default=request.now,
          label=T('Created On'),writable=False,readable=False),
    Field('modified_on','datetime',default=request.now,
          label=T('Modified On'),writable=False,readable=False,
          update=request.now),
    Field('created_by',db.auth_user,default=auth.user_id,
          label=T('Created By'),writable=False,readable=False),
    Field('modified_by',db.auth_user,default=auth.user_id,
          label=T('Modified By'),writable=False,readable=False,
          update=auth.user_id),
    format='%(f_title)s',
    migrate=settings.migrate)

db.define_table('t_appointment_archive',db.t_appointment,Field('current_record','reference t_appointment'))


def geocode2(form):
    from gluon.tools import geocode
    lo,la= geocode(form.vars.f_location+' USA')
    form.vars.f_latitude=la
    form.vars.f_longitude=lo
