# -*- coding: utf-8 -*- 

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = 'Random Mazes'
response.subtitle = 'with web2py+processing.js'

##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
    [i, False, 
     URL(request.application,'default','index',args=i), []]
    for i in (10,20,30,40,50)]

response.menu.append(['Sudoku Solver',False,'http://web2py.com/sudoku'])
