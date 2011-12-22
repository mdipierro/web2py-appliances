# -*- coding: utf-8 -*-

response.title = "Doc Net"
response.subtitle = "Trust your doctor"

response.menu = [('Home', False, URL(request.application,'default','index'))]

if auth.user and auth.user.patient:
    response.menu.append(('Your backlog', False, URL(request.application,'default','backlog',args=auth.user.id)))

if auth.user and (auth.user.doctor or auth.user.nurse or auth.user.administrator):
    response.menu.append(('New Patient', False, URL(request.application,'default','new_patient')))
    response.menu.append(('Search Patients', False, URL(request.application,'default','search')))
