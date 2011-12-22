response.title = "Friends"
response.subtitle = "yet another FB clone"
response.meta.keywords = "social network"
response.menu = [
    (T('Home'), False, URL('default','home')),
    (T('Wall'), False, URL('default','wall')),
    (T('Friends'), False, URL('default','friends')),
    (T('Search'), False, URL('default','search')),
    ]
