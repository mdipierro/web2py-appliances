# -*- coding: utf-8 -*-

#samlple variables as they would be defined in config file (models/plugin_issuetracker.py)
#plugin_issuetracker_host='test'
#plugin_issuetracker_user='bmbarnard'
#plugin_issuetracker_pwd=''
#plugin_issuetracker_projectid=1

#ping calls the ping function of the remote issue tracker application to test connectivity
def ping():

    #import the xmlrpcib library to be able to make rpc calls
    import xmlrpclib
    
    #attempting call using basic auth, still receiving 500 Errors
    #server=xmlrpclib.ServerProxy('http://b@b.com:yitbos@127.0.0.1:8000/issue_tracker/services/call/xmlrpc', verbose=True)
    server=xmlrpclib.ServerProxy(plugin_issuetracker_host)
    
    
    try:
        result=server.ping()
    except xmlrpclib.Fault, err:
        result = 'an error occurred '
        result += str(err.faultCode)
        result += err.faultString
    return dict(result=result) 

#index function for debuging the variables that are defined in the config file for plugin_issuetracker
#these are set at models/plugin_issuetracker.py
def index():    
    return dict(message='plugin_issuetracker config variables',
    issuetracker_host=plugin_issuetracker_host,
    issuetracker_user=plugin_issuetracker_user,
    issuetracker_pwd=plugin_issuetracker_pwd,
    issuetracker_projectid=plugin_issuetracker_projectid)

#submit new issue to remote issue_tracker
def postnewissue():
    
    #import the xmlrpcib library to be able to make rpc calls 
    import xmlrpclib 
    
    result=''    
   
    #define form for accepting variables for issue
    form = SQLFORM.factory(
    Field('summary', requires=IS_NOT_EMPTY()),
    Field('description', requires=IS_NOT_EMPTY()),
    Field('owner', requires=IS_NOT_EMPTY()))
    
    #handle submission
    if form.process().accepted:
       
        #get variables from config file (models/plugin_issuetracker.py)
        server=xmlrpclib.ServerProxy(plugin_issuetracker_host)
        projectid=issuetracker_projectid=plugin_issuetracker_projectid
       
        #get variables from the form
        summary=form.vars.summary
        description=form.vars.description
        owner=form.vars.owner

        #attempt to submit new issue to remote tracker
        try:
            result=server.newissue(projectid, summary, description, owner)
            result=str(result)
            result='New Issue Submitted. Issue Number: ' + result
            response.flash=result
        except xmlrpclib.Fault, err:
            result = 'an error occurred '
            result += str(err.faultCode)
            result += err.faultString
            response.flash='Error submitting issue to remote issue tracker'
    elif form.errors:
        response.flash='form has errors'
    
    return dict(form=form)


#submit new issue to remote issue_tracker, by receiving variables from a post
#most likely an ajax post
def post():
    import xmlrpclib
        
    #validate inputs
    if not request.vars.summary:
        return str('invalid value passed for summary, must not be null')    
    if not request.vars.description:
        return str('invalid value passed for description, must not be null')        
    if not request.vars.owner:    
        return str('invalid value passed for owner, must not be null')    
   
    #get static project and service variables from config file models/plugin_trackter.py
    server=xmlrpclib.ServerProxy(plugin_issuetracker_host)
    projectid=issuetracker_projectid=plugin_issuetracker_projectid
       
    #get variables from post
    summary=request.vars.summary
    description=request.vars.description
    owner=request.vars.owner

    #attempt to submit new issue to remote tracker
    try:
        result=server.newissue(projectid, summary, description, owner)
        result=str(result)
        result='New Issue Submitted. Issue Number: ' + result
    except xmlrpclib.Fault, err:
        result = 'an error occurred '
        result += str(err.faultCode)
        result += err.faultString
    return str(result)

#placeholder
def postajax():
    return dict(test='test')
