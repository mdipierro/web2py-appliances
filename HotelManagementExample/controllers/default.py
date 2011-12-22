# -*- coding: utf-8 -*-

def user():
    return dict(form = auth())

def download():
    return response.download(request, 
                             db)

def call():
    session.forget()
    return service()

def error():
    return dict()
    
@auth.requires_signature()
def data():
    return dict(form=crud())

def index():
    return dict()

blog_category = db.blog_category

def blog_category_index():
    return __index_0(blog_category)

blog = db.blog
blog_status = db.blog.status
blog_active = db.blog.is_active
blog_index = 'blog_index'
blog_draft = 'blog_draft'
blog_add = 'blog_add'
blog_edit = 'blog_edit'
blog_show = 'blog_show'
blog_search = 'blog_search'
blog_manage = 'blog_manage'

def blog_index():
    return __index_2(blog, 
                     blog_draft, 
                     blog_add, 
                     blog_search, 
                     blog_show, 
                     blog_manage,
                     blog_status,
                     blog_active)

def blog_draft():
    return __draft_0(blog, 
                     blog_index, 
                     blog_add, 
                     blog_search, 
                     blog_show, 
                     blog_manage,
                     blog_status,
                     blog_active)

def blog_add():
    return __add_2(blog, 
                   blog_index, 
                   blog_draft, 
                   blog_search, 
                   blog_manage)

def blog_edit():
    return __edit_1(blog, 
                    blog_index, 
                    blog_draft, 
                    blog_add, 
                    blog_search, 
                    blog_show)

def blog_show():
    return __show_1(blog, 
                    blog_index, 
                    blog_draft, 
                    blog_add, 
                    blog_search, 
                    blog_edit)

def blog_search():
    return __search_1(blog, 
                      blog_index, 
                      blog_draft, 
                      blog_add, 
                      blog_manage)

def blog_manage():
    return __manage_1(blog, 
                      blog_index, 
                      blog_draft, 
                      blog_add, 
                      blog_search)

def blog_like():
    return __like(blog)

blog_comment = db.blog_comment
blog_comment_blog_id = db.blog_comment.blog_id
blog_comment_active = db.blog_comment.is_active

def blog_comment_add():
    return __add_3(blog, 
                   blog_index, 
                   blog_comment, 
                   blog_comment_blog_id)

def blog_comment_show():
    return __show_2(blog, 
                    blog_index, 
                    blog_comment, 
                    blog_comment_blog_id, 
                    blog_comment_active)

def blog_comment_like():
    return __like(blog_comment)

booking = db.booking

def booking_index():
    return __index_0(booking)

branch_rating = db.branch_rating

def branch_rating_index():
    return __index_0(branch_rating)

branch = db.branch
branch_active = db.branch.is_active
branch_index = 'branch_index'
branch_add = 'branch_add'
branch_edit = 'branch_edit'
branch_show = 'branch_show'
branch_search = 'branch_search'
branch_manage = 'branch_manage'

def branch_index():
    return __index_1(branch, 
                     branch_add, 
                     branch_search, 
                     branch_show, 
                     branch_manage,
                     branch_active)

def branch_add():
    return __add_0(branch, 
                   branch_index, 
                   branch_search, 
                   branch_manage)

def branch_edit():
    return __edit_0(branch, 
                    branch_index, 
                    branch_add, 
                    branch_search, 
                    branch_show)

def branch_show():
    return __show_0(branch, 
                    branch_index, 
                    branch_add, 
                    branch_search, 
                    branch_edit)

def branch_search():
    return __search_0(branch, 
                      branch_index, 
                      branch_add, 
                      branch_manage)

def branch_manage():
    return __manage_0(branch, 
                      branch_index, 
                      branch_add, 
                      branch_search)

def branch_like():
    return __like(branch)

branch_comment = db.branch_comment
branch_comment_branch_id = db.branch_comment.branch_id
branch_comment_active = db.branch_comment.is_active

def branch_comment_add():
    return __add_3(branch, 
                   branch_index, 
                   branch_comment, 
                   branch_comment_branch_id)

def branch_comment_show():
    return __show_2(branch, 
                    branch_index, 
                    branch_comment, 
                    branch_comment_branch_id, 
                    branch_comment_active)

def branch_comment_like():
    return __like(branch_comment)

check_in = db.check_in

def check_in_index():
    return __index_0(check_in)

check_out = db.check_out

def check_out_index():
    return __index_0(check_out)

floor = db.floor

def floor_index():
    return __index_0(floor)

guest = db.guest

def guest_index():
    return __index_0(guest)

news_category = db.news_category

def news_category_index():
    return __index_0(news_category)

news = db.news
news_active = db.news.is_active
news_index = 'news_index'
news_add = 'news_add'
news_edit = 'news_edit'
news_show = 'news_show'
news_search = 'news_search'
news_manage = 'news_manage'

def news_index():
    return __index_1(news, 
                     news_add, 
                     news_search, 
                     news_show, 
                     news_manage,
                     news_active)

def news_add():
    return __add_0(news, 
                   news_index, 
                   news_search, 
                   news_manage)

def news_edit():
    return __edit_0(news, 
                    news_index, 
                    news_add, 
                    news_search, 
                    news_show)

def news_show():
    return __show_0(news, 
                    news_index, 
                    news_add, 
                    news_search, 
                    news_edit)

def news_search():
    return __search_0(news, 
                      news_index, 
                      news_add, 
                      news_manage)

def news_manage():
    return __manage_0(news, 
                      news_index, 
                      news_add, 
                      news_search)

def news_like():
    return __like(news)

news_comment = db.news_comment
news_comment_news_id = db.news_comment.news_id
news_comment_active = db.news_comment.is_active

def news_comment_add():
    return __add_3(news, 
                   news_index, 
                   news_comment, 
                   news_comment_news_id)

def news_comment_show():
    return __show_2(news, 
                    news_index, 
                    news_comment, 
                    news_comment_news_id, 
                    news_comment_active)

def news_comment_like():
    return __like(news_comment)

photo_album = db.photo_album

def photo_album_index():
    return __index_0(photo_album)

photo = db.photo
photo_active = db.photo.is_active
photo_index = 'photo_index'
photo_add = 'photo_add'
photo_edit = 'photo_edit'
photo_show = 'photo_show'
photo_search = 'photo_search'
photo_manage = 'photo_manage'

def photo_index():
    return __index_1(photo, 
                     photo_add, 
                     photo_search, 
                     photo_show, 
                     photo_manage,
                     photo_active)

def photo_add():
    return __add_0(photo, 
                   photo_index, 
                   photo_search, 
                   photo_manage)

def photo_edit():
    return __edit_0(photo, 
                    photo_index, 
                    photo_add, 
                    photo_search, 
                    photo_show)

def photo_show():
    return __show_0(photo, 
                    photo_index, 
                    photo_add, 
                    photo_search, 
                    photo_edit)

def photo_search():
    return __search_0(photo, 
                      photo_index, 
                      photo_add, 
                      photo_manage)

def photo_manage():
    return __manage_0(photo, 
                      photo_index, 
                      photo_add, 
                      photo_search)

def photo_like():
    return __like(photo)

photo_comment = db.photo_comment
photo_comment_photo_id = db.photo_comment.photo_id
photo_comment_active = db.photo_comment.is_active

def photo_comment_add():
    return __add_3(photo, 
                   photo_index, 
                   photo_comment, 
                   photo_comment_photo_id)

def photo_comment_show():
    return __show_2(photo, 
                    photo_index, 
                    photo_comment, 
                    photo_comment_photo_id, 
                    photo_comment_active)

def photo_comment_like():
    return __like(photo_comment)

room_category = db.room_category

def room_category_index():
    return __index_0(room_category)

room_status = db.room_status

def room_status_index():
    return __index_0(room_status)

room = db.room
room_active = db.room.is_active
room_index = 'room_index'
room_add = 'room_add'
room_edit = 'room_edit'
room_show = 'room_show'
room_search = 'room_search'
room_manage = 'room_manage'

def room_index():
    return __index_1(room, 
                     room_add, 
                     room_search, 
                     room_show, 
                     room_manage,
                     room_active)

def room_add():
    return __add_0(room, 
                   room_index, 
                   room_search, 
                   room_manage)

def room_edit():
    return __edit_0(room, 
                    room_index, 
                    room_add, 
                    room_search, 
                    room_show)

def room_show():
    return __show_0(room, 
                    room_index, 
                    room_add, 
                    room_search, 
                    room_edit)

def room_search():
    return __search_0(room, 
                      room_index, 
                      room_add, 
                      room_manage)

def room_manage():
    return __manage_0(room, 
                      room_index, 
                      room_add, 
                      room_search)

def room_like():
    return __like(room)

room_comment = db.room_comment
room_comment_room_id = db.room_comment.room_id
room_comment_active = db.room_comment.is_active

def room_comment_add():
    return __add_3(room, 
                   room_index, 
                   room_comment, 
                   room_comment_room_id)

def room_comment_show():
    return __show_2(room, 
                    room_index, 
                    room_comment, 
                    room_comment_room_id, 
                    room_comment_active)

def room_comment_like():
    return __like(room_comment)

cleaning = db.cleaning

def cleaning_index():
    return __index_0(cleaning)

video_category = db.video_category

def video_category_index():
    return __index_0(video_category)

video = db.video
video_active = db.video.is_active
video_comment = db.video_comment
video_comment_video_id = db.video_comment.video_id
video_comment_active = db.video_comment.is_active
video_index = 'video_index'
video_add = 'video_add'
video_edit = 'video_edit'
video_show = 'video_show'
video_search = 'video_search'
video_manage = 'video_manage'

def video_index():
    return __index_1(video, 
                     video_add, 
                     video_search, 
                     video_show, 
                     video_manage,
                     video_active)

def video_add():
    return __add_0(video, 
                   video_index, 
                   video_search, 
                   video_manage)

def video_edit():
    return __edit_0(video, 
                    video_index, 
                    video_add, 
                    video_search, 
                    video_show)

def video_show():
    return __show_0(video, 
                    video_index, 
                    video_add, 
                    video_search, 
                    video_edit)

def video_search():
    return __search_0(video, 
                      video_index, 
                      video_add, 
                      video_manage)

def video_manage():
    return __manage_0(video, 
                      video_index, 
                      video_add, 
                      video_search)

def video_like():
    return __like(video)

video_comment = db.video_comment
video_comment_video_id = db.video_comment.video_id
video_comment_active = db.video_comment.is_active

def video_comment_add():
    return __add_3(video, 
                   video_index, 
                   video_comment, 
                   video_comment_video_id)

def video_comment_show():
    return __show_2(video, 
                    video_index, 
                    video_comment, 
                    video_comment_video_id, 
                    video_comment_active)

def video_comment_like():
    return __like(video_comment)
