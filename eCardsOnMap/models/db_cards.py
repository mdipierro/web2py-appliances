GOOGLEMAP_KEY='ABQIAAAAnfs7bKE82qgb3Zc2YyS-oBT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSySz_REpPq-4WZA27OwgbtyR3VcA' # localhost
GOOGLEMAP_KEY='ABQIAAAAT5em2PdsvF3z5onQpCqv0RQKjFa1yJagLmzGcZ4UA6Ce9BDiWhSxvi4hSIQsWixy4LcFJtTrQTFuhg' # web2py.com

db.define_table('postcard',
    Field('created_by',db.auth_user,default=auth.user_id,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False),
    Field('from_nickname',default=('%(first_name)s %(last_name)s' % auth.user) if auth.user else ''),
    Field('from_location',requires=IS_NOT_EMPTY()),
    Field('latitude','double'),
    Field('longitude','double'),
    Field('image','upload'),
    Field('comment','text'))
