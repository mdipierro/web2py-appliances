from gluon.contrib.populate import populate
if db(db.auth_user).isempty():
    populate(db.blog_category, 
             100)
    db.branch_rating.bulk_insert([{'rating' : 'One Star'}, 
                                  {'rating' : 'Two Stars'}, 
                                  {'rating' : 'Three Stars'}, 
                                  {'rating' : 'Four Stars'}, 
                                  {'rating' : 'Five Stars'}])
    populate(db.branch, 
             100)
    populate(db.floor, 
             100)
    populate(db.guest, 
             100)
    populate(db.news_category, 
             100)
    populate(db.news, 
             100)
    populate(db.photo_album, 
             100)
    db.room_category.bulk_insert([{'category' : 'Single'}, 
                                  {'category' : 'Double'}, 
                                  {'category' : 'Suite'}])
    db.room_status.bulk_insert([{'status' : 'Available'}, 
                                {'status' : 'Booking'}, 
                                {'status' : 'Using'}, 
                                {'status' : 'Cleaning'}])
    populate(db.room, 
             100)
    populate(db.booking, 
             100)
    populate(db.check_in, 
             100)
    populate(db.check_out, 
             100)
    populate(db.cleaning, 
             100)
    populate(db.video_category, 
             100)
    auth.add_group('Manager', 
                   'Manager')
    auth.add_group('Admin', 
                   'Admin')
    auth.add_membership('1', 
                        '1')
    auth.add_membership('2', 
                        '1')
    auth.add_membership('2', 
                        '2')
    db.auth_user.bulk_insert([{'first_name' : 'Manager', 
                               'last_name' : 'Manager', 
                               'email' : 'manager@linux.vm', 
                               'password' : db.auth_user.password.validate('password')[0]}, 
                              {'first_name' : 'Admin', 
                               'last_name' : 'Admin', 
                               'email' : 'admin@linux.vm', 
                               'password' : db.auth_user.password.validate('password')[0]}])
