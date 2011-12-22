# -*- coding: utf-8 -*-

#new issue service accepts input for projectid, summary, description, and onwer and inserts a record
#to the issues table.
@service.xmlrpc
def newissue(pid, smy, des, own):
    from gluon.utils import web2py_uuid 
    
    #set variables
    projectIn=pid
    summaryIn=smy
    descriptionIn=des
    ownerIn=own
    statusIn='New'
    uuidIn=web2py_uuid()
    
    #insert to db
    result=db.issue.insert(project=projectIn, summary=summaryIn, description=descriptionIn, status=statusIn, owner=ownerIn, uuid=uuidIn)
    
    #return result
    return str(result)

#ping function returns a simple string, and the hostname this service is responding from
#this function is only for debugging purposes and simply returns a string to provide confirmation
#of connectivity
@service.xmlrpc
def ping():
    from socket import gethostname
    return 'successful response from issue_tracker service at: ' + gethostname()
    return 'test'


#service call handler
#@auth.requires_login
def call():
    session.forget()
    return service()
