# -*- coding: utf-8 -*-

"""
submit new issue to remote issue_tracker, by receiving variables from a post
most likely an ajax post
"""
def postnew():
    import xmlrpclib
        
    """validate inputs"""
    if not request.vars.summary:
        return str('invalid value passed for summary, must not be null')    
    if not request.vars.description:
        return str('invalid value passed for description, must not be null')        
    if not request.vars.owner:    
        return str('invalid value passed for owner, must not be null')    
   
    """get static project and service variables from config file models/plugin_trackter.py"""
    server=xmlrpclib.ServerProxy(plugin_issuetracker_host)
    projectid=issuetracker_projectid=plugin_issuetracker_projectid
       
    """get variables from post"""
    summary=request.vars.summary
    description=request.vars.description
    owner=request.vars.owner

    """attempt to submit new issue to remote tracker"""
    try:
        result=server.newissue(projectid, summary, description, owner)
        result=str(result)
        result='New Issue Submitted. Issue Number: ' + result
    except xmlrpclib.Fault, err:
        result = 'an error occurred '
        result += str(err.faultCode)
        result += err.faultString
    return str(result)
