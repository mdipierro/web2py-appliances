# -*- coding: utf-8 -*- 

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('customize me!')

##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
    ['Index', False, URL(request.application,'default','index')],
    ['Music', False, URL(request.application,'default','list_music')],
    ['Programs', False, URL(request.application,'default','list_programs')],
    ]

if not auth.user:
    response.menu+=[
    ['login',False, URL(request.application,'default','user/login')],
    ['register',False, URL(request.application,'default','user/register')],
    ['lost password?',False, URL(request.application,'default','user/request_reset_password')],
    ]
else:
    response.menu+=[
    ['logout',False, URL(request.application,'default','user/logout')],
    ['change password',False, URL(request.application,'default','user/change_password')],
    ['edit profile',False, URL(request.application,'default','user/profile')],
]
