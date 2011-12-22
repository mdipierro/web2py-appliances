response.menu=[
   (T('Home'),False,URL('default','index')),
   (T('Cart'),False,URL('default','cart')),
   (T('Buy'),False,URL('default','buy')),
   (T('My Orders'),False,URL('default','myorders')),   
]
if auth.user and auth.has_membership(role='manager'):
     response.menu.append((T('Manage Products'),False,URL('default','products')))
     response.menu.append((T('Manage Users'),False,URL('default','users')))
