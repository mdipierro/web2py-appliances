#from gluon.debug import dbg
from models_tools import start_datetime, end_datetime

db.define_table('calendar_duration',
    Field('name', label=T('Name'), notnull=True),
    Field('start_hour','time',label=T('Start hour')),
    Field('duration_in_minutes', 'integer'),
    format='%(name)s'
    )

db.define_table('calendar_contact',
    Field('name', label=T('Name'), notnull=True),
    Field('email', requires=IS_EMAIL(), label=T('Email')),
    Field('phone_number', requires=IS_MATCH('[\d\-\+\(\)\.\ ]+'), label=T('Phone number')),
    Field('address', 'text', label=T('Address')),
    format='%(name)s'
    )

db.define_table('calendar_event',
   Field('page', 'reference page', readable=False, writable=False, label=T('Page')),
   Field('contact', 'reference calendar_contact', readable=False, writable=False, label=T('Contact')),
   Field('title', readable=False, writable=False, label=T('Title')),
   Field('start_date','date',label=T('Start date'), notnull=True),
   Field('duration','reference calendar_duration',label=T('Duration')),
   Field('is_confirmed', 'boolean',label=T('Is confirmed (visible in calendar)'), readable=False, writable=False, default=False),
   Field.Method('start_datetime', start_datetime),
   Field.Method('end_datetime', end_datetime),
   format='%(title)s'
   )
db.calendar_event.page.requires = IS_IN_DB(db,db.page.id, '%(title)s', zero=T('<Empty>'))
db.calendar_event.contact.requires = IS_IN_DB(db,db.calendar_contact.id, '%(name)s', zero=T('<Empty>'))
db.calendar_event.duration.requires = IS_IN_DB(db,db.calendar_duration.id, '%(name)s', zero=T('<Empty>'))