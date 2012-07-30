# -*- coding: utf-8 -*-


###############################################################################
# web2py modelless scaffold app
# Bruno Cezar Rocha <rochacbruno@gmail.com>
#
# Posts
#
# in each controller you choose which handlers to import
###############################################################################

from handlers.post import Post


def index():
    post = Post('list_all')
    return post.render("mytheme/listposts")


def new():
    post = Post('create_new')
    return post.render("mytheme/newpost")


def edit():
    post = Post()
    post.edit_post(request.args(0))
    return post.render("mytheme/editpost")


def show():
    post = Post()
    post.show(request.args(0))
    return post.render("mytheme/showpost")
