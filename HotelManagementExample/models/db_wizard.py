# -*- coding: utf-8 -*-

db.define_table('blog_category', 
                Field('category', 
                      label = T('Category')
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_blog_category ON blog_category (id, category);')

db.define_table('blog_category_archive', 
                db.blog_category, 
                Field('current_record', 
                      'reference blog_category')
                )

db.define_table('blog', 
                Field('title', 
                      label = T('Title')
                      ),
                Field('content', 
                      'text', 
                      label = T('Content')
                      ),
                Field('category_id', 
                      db.blog_category,
                      label = T('Category ID')
                      ), 
                Field('status', 
                      'list:string', 
                      label = T('Status')
                      ),
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_blog ON blog (id, title);')

db.define_table('blog_archive', 
                db.blog, 
                Field('current_record', 
                      'reference blog')
                )

db.define_table('blog_comment', 
                Field('blog_id', 
                      db.blog, 
                      label = T('Blog ID')
                      ),
                Field('comment', 
                      'text', 
                      label = T('Comment')
                      ), 
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )

db.define_table('branch_rating',
                Field('rating', 
                      label = T('Rating')
                      ),
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_branch_rating ON branch_rating (id, rating);')

db.define_table('branch_rating_archive', 
                db.branch_rating, 
                Field('current_record', 
                      'reference branch_rating')
                )

db.define_table('branch', 
                Field('address', 
                      'text', 
                      label = T('Address')
                      ),
                Field('phone', 
                      label = T('Phone')
                      ),
                Field('fax', 
                      label = T('Fax')
                      ), 
                Field('rating_id', 
                      db.branch_rating,
                      label = T('Rating ID')
                      ), 
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_branch ON branch (id, address);')

db.define_table('branch_archive', 
                db.branch, 
                Field('current_record', 
                      'reference branch')
                )

db.define_table('branch_comment', 
                Field('branch_id', 
                      db.branch, 
                      label = T('Branch ID')
                      ),
                Field('comment', 
                      'text', 
                      label = T('Comment')
                      ), 
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )

db.define_table('floor',
                Field('no', 
                      'integer',
                      label = T('No')
                      ), 
                Field('status', 
                      label = T('Status')
                      ),
                Field('branch_id', 
                      db.branch, 
                      label = T('Branch ID')
                      ),
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_floor ON floor (id, no);')

db.define_table('floor_archive', 
                db.floor, 
                Field('current_record', 
                      'reference floor')
                )

db.define_table('guest', 
                Field('name', 
                      label = T('Name')
                      ),
                Field('address', 
                      'text', 
                      label = T('Address')
                      ),
                Field('phone', 
                      label = T('Phone')
                      ),
                Field('mobile_phone', 
                      label = T('Mobile Phone')
                      ),
                Field('email', 
                      label = T('Email')
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_guest ON guest (id, name);')

db.define_table('guest_archive', 
                db.guest, 
                Field('current_record', 
                      'reference guest')
                )

db.define_table('news_category', 
                Field('category', 
                      label = T('Category')
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_news_category ON news_category (id, category);')

db.define_table('news_category_archive', 
                db.news_category, 
                Field('current_record', 
                      'reference news_category')
                )

db.define_table('news', 
                Field('title', 
                      label = T('Title')
                      ),
                Field('content', 
                      'text', 
                      label = T('Content')
                      ),
                Field('category_id', 
                      db.news_category,
                      label = T('Category ID')
                      ), 
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_news ON news (id, title);')

db.define_table('news_archive', 
                db.news, 
                Field('current_record', 
                      'reference news')
                )

db.define_table('news_comment', 
                Field('news_id', 
                      db.news, 
                      label = T('News ID')
                      ),
                Field('comment', 
                      'text', 
                      label = T('Comment')
                      ), 
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )

db.define_table('photo_album', 
                Field('album', 
                      label = T('Album')
                      ),
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_photo_album ON photo_album (id, album);')

db.define_table('photo_album_archive', 
                db.photo_album, 
                Field('current_record', 
                      'reference photo_album')
                )

db.define_table('photo', 
                Field('photo', 
                      'upload', 
                      label = T('Photo'),
                      uploadfield = 'photo_data'
                      ),
                Field('photo_data', 
                      'blob', 
                      label = T('Photo Data')
                      ),
                Field('caption', 
                      label = T('Caption')
                      ),
                Field('album_id', 
                      db.photo_album, 
                      label = T('Album ID')
                      ),
                Field('visibility', 
                      'list:string', 
                      label = T('Visibility')
                      ),
                Field('password', 
                      'password', 
                      label = T('Password')
                      ),
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_photo ON photo (id, caption);')

db.define_table('photo_archive', 
                db.photo, 
                Field('current_record', 
                      'reference photo')
                )

db.define_table('photo_comment', 
                Field('photo_id', 
                      db.photo, 
                      label = T('Photo ID')
                      ),
                Field('comment', 
                      'text',
                      label = T('Comment')
                      ),
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )

db.define_table('room_category', 
                Field('category',
                      label = T('Category')
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_room_category ON room_category (id, category);')

db.define_table('room_category_archive', 
                db.room_category, 
                Field('current_record', 
                      'reference room_category')
                )

db.define_table('room_status', 
                Field('status',
                      label = T('Status')
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_room_status ON room_status (id, status);')

db.define_table('room_status_archive', 
                db.room_status, 
                Field('current_record', 
                      'reference room_status')
                )

db.define_table('room',
                Field('no', 
                      'integer',
                      label = T('No')
                      ), 
                Field('category_id', 
                      db.room_category,
                      label = T('Category ID')
                      ), 
                Field('status_id', 
                      db.room_status,
                      label = T('Status ID')
                      ), 
                Field('floor_id', 
                      db.floor,
                      label = T('Floor ID')
                      ), 
                Field('branch_id', 
                      db.branch, 
                      label = T('Branch ID')
                      ), 
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_room ON room (id, no);')

db.define_table('room_archive', 
                db.room, 
                Field('current_record', 
                      'reference room')
                )

db.define_table('room_comment', 
                Field('room_id', 
                      db.room, 
                      label = T('Room ID')
                      ),
                Field('comment', 
                      'text', 
                      label = T('Comment')
                      ), 
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )

db.define_table('booking', 
                Field('from_date', 
                      'date', 
                      label = T('From Date')
                      ), 
                Field('to_date', 
                      'date', 
                      label = T('To Date')
                      ), 
                Field('room_id', 
                      db.room, 
                      label = T('Room ID')
                      ), 
                Field('guest_id', 
                      db.guest, 
                      label = T('Guest ID')
                      ),
                auth.signature
                )

db.define_table('check_in', 
                Field('room_id', 
                      db.room, 
                      label = T('Room ID')
                      ), 
                Field('guest_id', 
                      db.guest, 
                      label = T('Guest ID')
                      ),
                auth.signature
                )

db.define_table('check_out', 
                Field('room_id', 
                      db.room, 
                      label = T('Room ID')
                      ), 
                Field('guest_id', 
                      db.guest, 
                      label = T('Guest ID')
                      ),
                auth.signature
                )

db.define_table('cleaning', 
                Field('room_id', 
                      db.room, 
                      label = T('Room ID')
                      ),
                auth.signature
                )

db.define_table('video_category', 
                Field('category',
                      label = T('Category')
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_video_category ON video_category (id, category);')

db.define_table('video_category_archive', 
                db.video_category, 
                Field('current_record', 
                      'reference video_category')
                )
    
db.define_table('video', 
                Field('title', 
                      label = T('Title')
                      ),
                Field('description', 
                      'text', 
                      label = T('Description')
                      ),
                Field('video', 
                      'upload', 
                      uploadfield = 'video_data', 
                      label = T('Video')
                      ),
                Field('video_data', 
                      'blob', 
                      label = T('Video Data')
                      ),
                Field('category_id', 
                      db.video_category,
                      label = T('Category ID')
                      ), 
                Field('visibility', 
                      'list:string', 
                      label = T('Visibility')
                      ),
                Field('password', 
                      'password', 
                      label = T('Password')
                      ),
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )
                
db.executesql('CREATE INDEX IF NOT EXISTS idx_video ON video (id, title);')

db.define_table('video_archive', 
                db.video, 
                Field('current_record', 
                      'reference video')
                )

db.define_table('video_comment', 
                Field('video_id', 
                      db.video, 
                      label = T('Video ID')
                      ),
                Field('comment', 
                      'text', 
                      label = T('Comment')
                      ), 
                Field('like', 
                      'integer',
                      label = T('Like'),
                      default = 0,
                      writable = False
                      ), 
                auth.signature
                )
