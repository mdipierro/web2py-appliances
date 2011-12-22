# -*- coding: utf-8 -*-

response.title = settings.title
response.subtitle = settings.subtitle

response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.description = settings.description
response.meta.keywords = settings.keywords
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright © 2011'

response.menu = [(T('Home'), 
                  False, 
                  URL('index'),
                  []
                  ), 
                 (T('Branch Rating'), 
                  False, 
                  URL('branch_rating_index'),
                  []
                  ), 
                 (T('Branch'), 
                  False, 
                  URL('branch_index'),
                  []
                  ), 
                 (T('Floor'), 
                  False, 
                  URL('floor_index'),
                  []
                  ), 
                 (T('Room Category'), 
                  False, 
                  URL('room_category_index'),
                  []
                  ),
                 (T('Room Status'), 
                  False, 
                  URL('room_status_index'),
                  []
                  ),
                 (T('Room'), 
                  False, 
                  URL('room_index'),
                  []
                  ), 
                 (T('Guest'), 
                  False, 
                  URL('guest_index'),
                  []
                  ), 
                 (T('Booking'), 
                  False, 
                  URL('booking_index'),
                  []
                  ), 
                 (T('Check In'), 
                  False, 
                  URL('check_in_index'),
                  []
                  ), 
                 (T('Check Out'), 
                  False, 
                  URL('check_out_index'),
                  []
                  ),  
                 (T('Cleaning'), 
                  False, 
                  URL('cleaning_index'),
                  []
                  ), 
                 (T('News Category'), 
                  False, 
                  URL('news_category_index'),
                  []
                  ), 
                 (T('News'), 
                  False, 
                  URL('news_index'),
                  []
                  ), 
                 (T('Blog Category'), 
                  False, 
                  URL('blog_category_index'),
                  []
                  ), 
                 (T('Blog'), 
                  False, 
                  URL('blog_index'),
                  []
                  ), 
                 (T('Photo Album'), 
                  False, 
                  URL('photo_album_index'),
                  []
                  ), 
                 (T('Photo'), 
                  False, 
                  URL('photo_index'),
                  []
                  ), 
                 (T('Video Category'), 
                  False, 
                  URL('video_category_index'),
                  []
                  ), 
                 (T('Video'), 
                  False, 
                  URL('video_index'),
                  []
                  ), 
                 ]
