#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('customize me!')

response.menu = [
    ['home', False, URL('default','index')],
    ['docs', False, URL('static','semantic.pdf')],
    ['download', False, URL('static','web2py.plugin.rdf.w2p')],
    ]

