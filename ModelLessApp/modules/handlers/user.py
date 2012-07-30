# -*- coding: utf-8 -*-


###############################################################################
# web2py modelless scaffold app
# Bruno Cezar Rocha <rochacbruno@gmail.com>
#
# Posts
###############################################################################

from handlers.base import Base
from myapp import MyApp


class User(Base):
    def start(self):
        self.app = MyApp()
        self.auth = self.app.auth  # you need to access this to define users

    def list_all(self):
        self.context.posts = self.db(self.db.Post).select()

    def create_new(self):
        # permission is checked here
        if self.auth.has_membership("author", self.auth.user_id):
            self.context.form = SQLFORM(self.db.Post).process()
        else:
            self.context.form = "You can't post"

    def edit_post(self, post_id):
        post = self.db.Post[post_id]
        # permission is checked here
        if not post or post.author != self.auth.user_id:
            redirect(URL("post", "index"))
        self.context.form = SQLFORM(self.db.Post, post.id).process()

    def show(self, post_id):
        self.context.post = self.db.Post[post_id]
        if not self.context.post:
            redirect(URL("post", "index"))
