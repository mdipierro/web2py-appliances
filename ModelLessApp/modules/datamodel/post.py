# -*- coding: utf-8 -*-

###############################################################################
# web2py modelless scaffold app
# Bruno Cezar Rocha <rochacbruno@gmail.com>
#
# Posts datamodel
###############################################################################

from gluon.dal import Field
from basemodel import BaseModel
from gluon.validators import IS_NOT_EMPTY, IS_SLUG
from gluon import current
from plugin_ckeditor import CKEditor


class Post(BaseModel):
    tablename = "blog_post"

    def set_properties(self):
        ckeditor = CKEditor(self.db)
        T = current.T
        self.fields = [
            Field("author", "reference auth_user"),
            Field("title", "string", notnull=True),
            Field("description", "text"),
            Field("body_text", "text", notnull=True),
            Field("slug", "text", notnull=True),
        ]

        self.widgets = {
            "body_text": ckeditor.widget
        }

        self.visibility = {
            "author": (False, False)
        }

        self.representation = {
            "body_text": lambda row, value: XML(value)
        }

        self.validators = {
            "title": IS_NOT_EMPTY(),
            "body_text": IS_NOT_EMPTY()
        }

        self.computations = {
          "slug": lambda r: IS_SLUG()(r.title)[0],
        }

        self.labels = {
            "title": T("Your post title"),
            "description": T("Describe your post (markmin allowed)"),
            "body_text": T("The content")
        }
