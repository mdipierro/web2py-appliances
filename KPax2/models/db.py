import random
import time; now=time.time()
import datetime;
timestamp=datetime.datetime.today()
today=datetime.date.today()

db=DAL("sqlite://main.db")

from gluon.tools import Auth
auth = Auth(db)

auth.settings.extra_fields['auth_user']=[Field('name',compute=lambda r: "%(first_name)s %(last_name)s" % r)]
auth.define_tables()
