# blog_category
db.blog_category.category.requires = [IS_NOT_EMPTY(), 
                                      IS_NOT_IN_DB(db, 
                                                   'blog_category.category')]

# blog
db.blog.title.requires = [IS_NOT_EMPTY(), 
                          IS_NOT_IN_DB(db, 
                                       'blog.title')]
db.blog.content.requires = [IS_NOT_EMPTY(), 
                            IS_NOT_IN_DB(db, 
                                         'blog.content')]
db.blog.category_id.requires = IS_IN_DB(db, 
                                        db.blog_category.id, 
                                        '%(category)s')
db.blog.status.requires = IS_IN_SET(('Published', 
                                     'Draft'))

# blog_comment
db.blog_comment.blog_id.requires = IS_IN_DB(db, 
                                            db.blog.id, 
                                            '%(title)s')
db.blog_comment.comment.requires = IS_NOT_EMPTY()

# branch_rating
db.branch_rating.rating.requires = [IS_NOT_EMPTY(), 
                                    IS_NOT_IN_DB(db, 
                                                 'branch_rating.rating')]

# branch
db.branch.address.requires = [IS_NOT_EMPTY(), 
                              IS_NOT_IN_DB(db, 
                                           'branch.address')]
db.branch.phone.requires = [IS_NOT_EMPTY(), 
                            IS_NOT_IN_DB(db, 
                                         'branch.phone')]
db.branch.fax.requires = [IS_NOT_EMPTY(), 
                          IS_NOT_IN_DB(db, 
                                       'branch.fax')]
db.branch.rating_id.requires = IS_IN_DB(db, 
                                        db.branch_rating.id, 
                                        '%(rating)s')

# branch_comment
db.branch_comment.branch_id.requires = IS_IN_DB(db, 
                                                db.branch.id, 
                                                '%(address)s')
db.branch_comment.comment.requires = IS_NOT_EMPTY()

# floor
db.floor.no.requires = IS_NOT_EMPTY()
db.floor.status.requires = [IS_NOT_EMPTY(), 
                            IS_NOT_IN_DB(db, 
                                         'floor.status')]
db.floor.branch_id.requires = IS_IN_DB(db, 
                                       db.branch.id, 
                                       '%(address)s')

# guest
db.guest.name.requires = IS_NOT_EMPTY()
db.guest.address.requires = IS_NOT_EMPTY()
db.guest.phone.requires = IS_NOT_EMPTY()
db.guest.mobile_phone.requires = [IS_NOT_EMPTY(), 
                                  IS_NOT_IN_DB(db, 
                                               'guest.mobile_phone')]
db.guest.email.requires = [IS_NOT_EMPTY(), 
                           IS_NOT_IN_DB(db, 
                                        'guest.email')]

# news_category
db.news_category.category.requires = [IS_NOT_EMPTY(), 
                                      IS_NOT_IN_DB(db, 
                                                   'news_category.category')]

# news
db.news.title.requires = [IS_NOT_EMPTY(), 
                          IS_NOT_IN_DB(db, 
                                       'news.title')]
db.news.content.requires = [IS_NOT_EMPTY(), 
                            IS_NOT_IN_DB(db, 
                                         'news.content')]
db.news.category_id.requires = IS_IN_DB(db, 
                                        db.news_category.id, 
                                        '%(category)s')

# news_comment
db.news_comment.news_id.requires = IS_IN_DB(db, 
                                            db.news.id, 
                                            '%(title)s')
db.news_comment.comment.requires = IS_NOT_EMPTY()

# photo_album
db.photo_album.album.requires = [IS_NOT_EMPTY(), 
                                 IS_NOT_IN_DB(db, 
                                              'photo_album.album')]

# photo
db.photo.photo.requires = [IS_NOT_EMPTY(), 
                           IS_IMAGE()]
db.photo.photo_data.requires = IS_NOT_EMPTY()
db.photo.caption.requires = [IS_NOT_EMPTY(), 
                             IS_NOT_IN_DB(db, 
                                          'photo.caption')]
db.photo.album_id.requires = IS_IN_DB(db, 
                                      db.photo_album.id, 
                                      '%(album)s')
db.photo.visibility.requires = IS_IN_SET(('Public', 
                                          'Private', 
                                          'Protected'))
db.photo.password.requires = IS_EMPTY_OR(IS_STRONG(min = 6, 
                                                   special = 1, 
                                                   upper = 1))

# photo_comment
db.photo_comment.photo_id.requires = IS_IN_DB(db, 
                                              db.photo.id, 
                                              '%(caption)s')
db.photo_comment.comment.requires = IS_NOT_EMPTY()

# room_category
db.room_category.category.requires = [IS_NOT_EMPTY(), 
                                      IS_NOT_IN_DB(db, 
                                                   'room_category.category')]

# room_status
db.room_status.status.requires = [IS_NOT_EMPTY(), 
                                  IS_NOT_IN_DB(db, 
                                               'room_status.status')]

# room
db.room.no.requires = IS_NOT_EMPTY()
db.room.category_id.requires = IS_IN_DB(db, 
                                        db.room_category.id, 
                                        '%(category)s')
db.room.status_id.requires = IS_IN_DB(db, 
                                      db.room_status.id, 
                                      '%(status)s')
db.room.floor_id.requires = IS_IN_DB(db, 
                                     db.floor.id, 
                                     '%(no)s')
db.room.branch_id.requires = IS_IN_DB(db, 
                                      db.branch.id, 
                                      '%(address)s')

# room_comment
db.room_comment.room_id.requires = IS_IN_DB(db, 
                                            db.room.id, 
                                            '%(no)s')
db.room_comment.comment.requires = IS_NOT_EMPTY()

# booking
db.booking.from_date.requires = IS_DATE()
db.booking.to_date.requires = IS_DATE()
db.booking.room_id.requires = IS_IN_DB(db, 
                                       db.room.id, 
                                       '%(no)s')
db.booking.guest_id.requires = IS_IN_DB(db, 
                                        db.guest.id, 
                                        '%(name)s')

# check_in
db.check_in.room_id.requires = IS_IN_DB(db, 
                                        db.room.id, 
                                        '%(no)s')
db.check_in.guest_id.requires = IS_IN_DB(db, 
                                         db.guest.id, 
                                         '%(name)s')

# check_out
db.check_out.room_id.requires = IS_IN_DB(db, 
                                         db.room.id, 
                                         '%(no)s')
db.check_out.guest_id.requires = IS_IN_DB(db, 
                                          db.guest.id, 
                                          '%(name)s')

# cleaning
db.cleaning.room_id.requires = IS_IN_DB(db, 
                                        db.room.id, 
                                        '%(no)s')

# video_category
db.video_category.category.requires = [IS_NOT_EMPTY(), 
                                       IS_NOT_IN_DB(db, 
                                                    'video_category.category')]

# video
db.video.title.requires = IS_NOT_EMPTY()
db.video.description.requires = IS_NOT_EMPTY()
db.video.video.requires = [IS_NOT_EMPTY(),
                           IS_UPLOAD_FILENAME(extension = 'flv')]
db.video.video_data.requires = IS_NOT_EMPTY()
db.video.category_id.requires = IS_IN_DB(db, 
                                         db.video_category.id, 
                                         '%(category)s')
db.video.visibility.requires = IS_IN_SET(('Public', 
                                          'Private', 
                                          'Protected'))
db.video.password.requires = IS_EMPTY_OR(IS_STRONG(min = 6, 
                                                   special = 1, 
                                                   upper = 1))

# video_comment
db.video_comment.video_id.requires = IS_IN_DB(db, 
                                              db.video.id, 
                                              '%(title)s')
db.video_comment.comment.requires = IS_NOT_EMPTY()
