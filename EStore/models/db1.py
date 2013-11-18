CURRENCY = '$'
INE = IS_NOT_EMPTY()

session.cart = session.cart or {}

auth.settings.extra_fields['auth_user'] = [
    Field('is_manager','boolean',default=True)
]
auth.define_tables(username=False, signature=False)
if auth.user: auth.user.is_manager = True

db.define_table(
    'product',
    Field('category'),
    Field('name',required=True),
    Field('description_short','text'),
    Field('description_long','text'),
    Field('private_info','text'),
    Field('unit_price','double'),
    Field('on_sale','boolean'),
    Field('rating','double'),
    Field('clicks','integer'),
    Field('image','upload'),
    Field('delivery',requires=IS_IN_SET(('normal','free','digital'))),
    Field('media_file','upload'),
    Field('rating','double'),
    Field('in_stock','integer'),
    Field('discount_2x','double'),
    Field('discount_3x','double'),
    Field('discount_4x','double'),
    Field('discount_5x','double'),
    Field('discount_10x','double'),
    Field('tax_rate','double',default=3.0),
    Field('volume','list:integer',default=0.0),
    Field('weight','double',default=0.0),
    format='%(name)s')

db.define_table(
    'inventory',
    Field('product','reference product'),
    Field('detail'),
    Field('code'),
    Field('description','text'),
    Field('quantity','integer'),
    Field('serial_codes','list:string'))

db.define_table(
    'cart_order',
    Field('billing_to',requires=INE),
    Field('billing_address',requires=INE),
    Field('billing_city',requires=INE),
    Field('billing_zip',requires=INE),
    Field('billing_country',requires=INE),
    Field('billing_phone'),
    Field('shipping_to',requires=INE),
    Field('shipping_address',requires=INE),
    Field('shipping_city',requires=INE),
    Field('shipping_zip',requires=INE),
    Field('shipping_country',requires=INE),
    Field('shipping_phone'),
    Field('shipping_instructions','text'),
    Field('shipping_type',requires=IS_IN_SET(('USPS','UPS','FEDEX'))),
    Field('total','double',readable=False,writable=False),
    Field('total_discount','double',readable=False,writable=False),
    Field('total_tax','double',readable=False,writable=False),
    Field('total_after_tax','double',readable=False,writable=False),
    Field('total_with_shipping',readable=False,writable=False),
    Field('amount_due','double',readable=False,writable=False),
    Field('amount_paid','double',readable=False,writable=False,default=0.0),
    auth.signature)

db.define_table(
    'payment',
    Field('cart_order','reference cart_order'),
    Field('payment_id'))

db.define_table(
    'shipping',
    Field('shipped_date','date'),
    Field('tracking_info'),
    Field('shipping_label'),
    Field('notes'))

db.define_table(
    'invoice_item',
    Field('invoice','reference invoice'),
    Field('quantity','double',default=1),
    Field('inventory','reference inventory'),
    Field('shipping','reference shipping'),
    db.product,
    db.inventory) # copy the prodoct, in case changes

def price_cart():    
    total_pretax = 0.0
    tax = 0.0
    volume = [0, 0, 0]
    weight = 0.0
    discount = 0.0
    for qty, product, inventory in session.cart.itervalues():
        price = product.unit_price*qty
        n, d = qty, 0.0
        if product.discount_10x:
            d += product.discount_10x*int(n/10)
            n -= 10*int(n/10)
        if n and product.discount_5x:
            d += product.discount_5x*int(n/5)
            n -= 5*int(n/5) 
        if n and product.discount_4x:
            d += product.discount_4x*int(n/4)
            n -= 4*int(n/4) 
        if n and product.discount_3x:
            d += product.discount_3x*int(n/3)
            n -= 3*int(n/3) 
        if n and product.discount_2x:
            d += product.discount_2x*int(n/2)
            n -= 2*int(n/2) 
        product.price = price
        total_pretax += price
        discount += d
        tax += product.tax_rate*(price-d)/100
        w = product.volume
        if product.delivery=='normal':
            if w and len(w)==3:
                for k in range(qty):
                    v = [x for x in volume or [0,0,0]]
                    v.sort()
                    volume = [v[0]+w[0],max(v[1],w[1]),max(v[2],w[2])]
                    volume.sort()
            if product.weight:
                weight += qty*product.weight
    if COMPANY_ADDRESS and session.checkout_form:        
        address2 = '%(shipping_address)s %(shipping_city)s %(shipping_zip)s %(shipping_country)s' % session.checkout_form
        shipping = compute_shipping(type, volume, weight, 
                                    COMPANY_ADDRESS, address2)
        total_with_shipping = total_pretax-discount+tax+shipping
    else:
        shipping = None
        total_with_shipping = None
    return dict(
        total = total_pretax,
        total_discount = discount,
        total_tax = tax, 
        total_with_tax = total_pretax-discount+tax, 
        total_volume = volume,
        total_weight = weight,
        total_with_shipping = total_with_shipping)

def group_rows(rows,table1,*tables):
    last = None
    new_rows = []
    for row in rows:
        row_table1 = row[table1]
        if not last or row_table1.id!=last.id:
            last = row_table1
            new_rows.append(last)
            for t in tables:
                last[t] = []
        for t in tables:
            last[t].append(row[t])
    return new_rows
