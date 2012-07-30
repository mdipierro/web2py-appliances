# -*- coding: utf-8 -*-


###############################################################################
# web2py modelless scaffold app
# Bruno Cezar Rocha <rochacbruno@gmail.com>
#
# Posts
###############################################################################

from handlers.base import Base
from myapp import MyApp
from datamodel.post import Post as PostModel
from gluon import SQLFORM, URL, redirect


class Post(Base):
    def start(self):
        self.app = MyApp()
        self.auth = self.app.auth  # you need to access this to define users
        self.db = self.app.db([PostModel])

        # this is needed to inject auth in template render
        # only needed to use auth.navbar()
        self.context.auth = self.auth

    def list_all(self):
        self.context.posts = self.db(self.db.Post).select(orderby=~self.db.Post.created_on)

    def create_new(self):
        # permission is checked here
        if self.auth.has_membership("author", self.auth.user_id):
            self.db.Post.author.default = self.auth.user_id
            self.context.form = SQLFORM(self.db.Post, formstyle='divs').process(onsuccess=lambda form: redirect(URL('show', args=form.vars.id)))
        else:
            self.context.form = "You can't post, only logged in users, members of 'author' group can post"

    def edit_post(self, post_id):
        post = self.db.Post[post_id]
        # permission is checked here
        if not post or post.author != self.auth.user_id:
            redirect(URL("post", "index"))
        self.context.form = SQLFORM(self.db.Post, post.id, formstyle='divs').process(onsuccess=lambda form: redirect(URL('show', args=form.vars.id)))

    def show(self, post_id):
        self.context.post = self.db.Post[post_id]
        if not self.context.post:
            redirect(URL("post", "index"))
