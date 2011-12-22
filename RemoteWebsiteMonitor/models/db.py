# try something like
import datetime
now=datetime.datetime.now()
db=DAL("sqlite://db.db")

db.define_table('web_site',Field('url',length=128))

db.define_table('failure',
   Field('url',length=128),
   Field('timestamp','datetime',default=now))
