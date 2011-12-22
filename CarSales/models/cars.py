# coding: utf8

# pre-defined validator
notempty=IS_NOT_EMPTY(error_message=e_m['empty'])

# definition of car makers
db.define_table('brand',
                Field('name', unique=True, notnull=True),
                format='%(name)s')

# definition of brand validators
db.brand.name.requires=[notempty, IS_NOT_IN_DB(db, 'brand.name',
                                               error_message=e_m['in_db'])]


# definition of car table
db.define_table('car',
                Field('brand', db.brand, notnull=True),
                Field('model', notnull=True),
                Field('year', 'integer', notnull=True),
                Field('color', notnull=True),
                Field('price', 'double'),
                Field('itens', 'list:string'),
                Field('status', notnull=True),
                Field('desc', 'text'),
                Field('pict', 'upload'),
                format='%(model)s - %(year)s - %(status)s'
                )

# validation of car
db.car.brand.requires=IS_IN_DB(db, 'brand.id','brand.name', 
                                 error_message=e_m['not_in_db'])
db.car.model.requires=notempty
db.car.year.requires=[notempty,IS_INT_IN_RANGE(request.now.year-20,request.now.year+2,
                                                 error_message=e_m['not_in_range'])]
db.car.color.requires=IS_IN_SET(colors)
db.car.itens.requires=IS_IN_SET(('Alarm','Lock','Sound System', 'Air'),multiple=True,
                                  error_message=e_m['not_in_set'])
db.car.status.requires=IS_IN_SET(statuses,error_message=e_m['not_in_set'])
db.car.pict.requires=IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg', 'png', '.gif'),
                                            error_message=e_m['image']))


# definition of client
db.define_table('client',
                Field('id_car', db.car),
                Field('name'),
                Field('email'),
                Field('tel'),
                Field('finance','boolean'),
                Field('change','boolean'),
                Field('date', 'datetime', default=request.now)
                )

# validation of client
db.client.name.requires=notempty
db.client.email.requires=IS_EMAIL(error_message=e_m['email'])
db.client.tel.requires=notempty

#formating client
db.client.name.label = 'Full name'
db.client.email.label = 'your e-mail'
db.client.tel.label = 'Your Telephone'
db.client.finance.label = 'I want to finance'
db.client.change.label = 'I want to give a car for change'
db.client.date.writable=False
db.client.date.readable=False
