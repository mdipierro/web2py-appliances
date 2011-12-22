if request.env.web2py_runtime_gae:            
    db = DAL('gae')                           
    session.connect(request, response, db=db) 
else:                                         
    db = DAL('sqlite://storage.sqlite')       

from gluon.tools import *
auth=Auth(globals(),db)                # authentication/authorization
auth.settings.hmac_key='<your secret key>'
auth.define_tables()                   # creates all needed tables
crud=Crud(globals(),db)                # for CRUD helpers using auth
service=Service(globals())             # for json, xml, jsonrpc, xmlrpc, amfrpc
