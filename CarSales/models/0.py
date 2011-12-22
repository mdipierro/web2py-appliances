# coding: utf8
db = DAL('sqlite://storage.sqlite')

from gluon.tools import Crud, Auth
crud=Crud(globals(), db)
auth=Auth(globals(), db)
auth.define_tables()

#auth.settings.actions_disabled.append('register')

e_m={
    'empty':'This is a required Field',
    'in_db':'This already exists in database',
    'not_in_db':'This does not exists in database',
    'email':'You have to insert a valid mail address',
    'image':'The file need to be an image',
    'not_in_set':'You need to chose a valid value',
    'not_in_range':'Type a number between %(min)s and %(max)s',
    }
            
config=dict(nmsite='Car Store', dscsite='The best car for your needs')

statuses =('New', 'Used')

colors=('Blue', 'Yellow', 'Green', 'Red',\
    'Silver', 'White', 'Black', 'Purple')
    
    

