# coding: utf8

from gluon.utils import web2py_uuid

db.define_table('event',
  Field('name',requires=IS_NOT_EMPTY()),
  Field('start','datetime'),
  Field('stop','datetime'),
  Field('description','text'),
  Field('uuid',default=web2py_uuid(),writable=False,readable=False),
  auth.signature,
  format="%(name)s")
  
db.event.is_active.readable=db.event.is_active.writable=False

db.define_table('rsvp',
  Field('event','reference event'),
  Field('attendee','reference auth_user'),
  Field('attendance',requires=IS_IN_SET(('yes','no','maybe'))),
  Field('comment','text'),
  auth.signature)

db.rsvp.is_active.readable=db.rsvp.is_active.writable=False
