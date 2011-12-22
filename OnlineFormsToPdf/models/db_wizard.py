### we prepend t_ to tablenames and f_ to fieldnames for disambiguity
import uuid

crud.settings.formstyle="table2cols"

########################################
db.define_table('t_form',
    Field('id','id',
          represent=lambda id:SPAN(id,' ',A('view',_href=URL('form_read',args=id)))),
    Field('f_name', type='string',
          label=T('Name')),
    Field('f_content', type='text',
          represent=lambda x: MARKMIN(x),
          comment='WIKI (markmin)',
          label=T('Content')),
    Field('f_public', type='boolean', default=False,
          label=T('Available to all users?')),
    Field('f_uuid',default=str(uuid.uuid4()),
          writable=False,readable=False),
    Field('f_created_on','datetime',default=request.now,
          label=T('Created On'),writable=False,readable=False),
    Field('f_modified_on','datetime',default=request.now,
          label=T('Modified On'),writable=False,readable=False,
          update=request.now),
    Field('f_created_by',db.auth_user,default=auth.user_id,
          label=T('Created By'),writable=False,readable=False),
    Field('f_modified_by',db.auth_user,default=auth.user_id,
          label=T('Modified By'),writable=False,readable=False,
          update=auth.user_id),
    format='%(f_name)s',
    migrate=settings.migrate)

db.t_form.f_name.default="Example: Job Application"
db.t_form.f_content.default="""
# Job Application
## Instuructions
- please complete the form
- export it in PDF
- print it
- sign it
- fax it to 111-111-1111
## Job Application Questionaire
### Personal data
--------
**first name:** | ``first_name``:input_text
**last name:** | ``last_name``:input_text
**email:** | ``email``:input_text
--------
### Skills
``skills``:input_area
### Signature
``accept``:input_bool Accept [[Confidentiality Agreement http://example.com]]

Signature: ..................................... Date: ``today``:input_date 
"""


