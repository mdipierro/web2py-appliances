# we need a table to store products
db.define_table('product',
   Field('name',notnull=True,unique=True),
   Field('price','double'),
   Field('description','text'),
   Field('image','upload'),
   Field('sortable','integer'),
   auth.signature,
   format='%(name)s')

# and one table to store sales of products to users
db.define_table('sale',
   Field('invoice'),
   Field('creditcard'),
   Field('buyer',db.auth_user),
   Field('product',db.product),
   Field('quantity','integer'),
   Field('price','double'),
   Field('shipped','boolean',default=False),
   Field('shipping_address'),
   Field('shipping_city'),
   Field('shipping_state'),
   Field('shipping_zip_code'),
   Field('shipping_date','datetime'),
   Field('delivery_date','datetime'),
   Field('tracking_number'),
   auth.signature),

# we also make a session cart, just in case
session.cart = session.cart or {}
