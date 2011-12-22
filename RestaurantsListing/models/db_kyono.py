# coding: utf8
db.define_table('restaurant',
    Field('name'),
    Field('owner_id',db.auth_user),
    Field('address1'),
    Field('address2'),
    Field('city'),
    Field('state'),
    Field('zip'),
    Field('phone'),
    Field('fax'),
    Field('website'),
    Field('map','text',comment='embed code for google map'),
    Field('about','text'),
    Field('is_special','boolean'),
    Field('special','text', comment='daily or weekly special menu here'),
    auth.signature,
    format='%(name)s')

db.restaurant.name.requires = IS_NOT_EMPTY()
db.restaurant.address1.requires = IS_NOT_EMPTY()
db.restaurant.city.requires = IS_NOT_EMPTY()
db.restaurant.state.requires = IS_NOT_EMPTY()
db.restaurant.zip.requires = IS_MATCH('\d{5}(\-\d{4})?')
db.restaurant.phone.requires = IS_MATCH('(\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$',error_message='not a valid phone number')

db.define_table('special',
    Field('restaurant_id', db.restaurant),
    Field('name'),
    Field('price','double'),
    Field('image','upload'),
    format='%(name)s')

db.special.name.requires = IS_NOT_EMPTY()
db.special.price.requires = IS_NOT_EMPTY()
db.special.image.requires = IS_IMAGE()

db.define_table('favorite',
    Field('user',db.auth_user, default=db.auth_user.id),
    Field('restaurant_id',db.restaurant))
