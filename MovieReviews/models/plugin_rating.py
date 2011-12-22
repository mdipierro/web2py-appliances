db.define_table('plugin_rating_master',
   Field('tablename'),
   Field('record_id','integer'),
   Field('rating','double'),
   Field('counter','integer'))

db.define_table('plugin_rating_aux',
   Field('master',db.plugin_rating_master),
   Field('rating','double'),
   Field('created_by',db.auth_user))

response.files.append(URL(r=request,c='static',
                          f='plugin_rating/jquery.rating.css'))
response.files.append(URL(r=request,c='static',
                          f='plugin_rating/jquery.rating.js'))

def plugin_rating(tablename,record_id=0):
    row=db(db.plugin_rating_master.tablename==tablename)\
        (db.plugin_rating_master.record_id==record_id).select().first()
    if not row:
        rating = 2
    else:
        rating = row.rating
    return TAG[''](DIV(_id='star1',_class='rating'),
                   SCRIPT("jQuery(document).ready(function(){jQuery('#star1').rating('%s',{maxvalue:5,curvalue:%s});});" % (URL(r=request,c='plugin_rating',f='rate',args=[tablename,record_id]),rating)))
