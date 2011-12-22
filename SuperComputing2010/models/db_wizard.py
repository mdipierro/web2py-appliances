### we prepend t_ to tablenames and f_ to fieldnames for disambiguity


########################################
db.define_table('t_experiment',
    Field('id','id',
          represent=lambda id:SPAN(id,' ',A('view',_href=URL('experiment_read',args=id)))),
    Field('f_name', type='string',
          label=T('Name')),
    Field('f_slits', type='list:string',
          label=T('Slits')),
    Field('f_description', type='text',
          represent=lambda x: MARKMIN(x),
          comment='WIKI (markmin)',
          label=T('Description')),
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
    format='%(f_name)s',
    migrate=settings.migrate)

db.define_table('t_experiment_archive',db.t_experiment,Field('current_record','reference t_experiment'))
