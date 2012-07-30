# -*- coding: utf-8 -*-

###############################################################################
# web2py modelless scaffold app
# Bruno Cezar Rocha <rochacbruno@gmail.com>
#
# This is the user datamodel
###############################################################################

from gluon.dal import Field
from basemodel import BaseAuth
from gluon.validators import *
from helpers.images import THUMBER
from gluon import current


class User(BaseAuth):
    def set_properties(self):
        T = current.T
        # take a look in basemodel to see the options allowed here
        # self.widgets, self.fields, self.validators etc....
        # only extra fields are defined here

        self.fields = [
                      # Person info
                      Field("nickname"),
                      Field("website", "string"),
                      Field("avatar", "upload"),
                      Field("thumbnail", "upload"),
                      Field("about", "text"),
                      Field("gender", "string"),
                      Field("birthdate", "date"),
                     ]

        # it sets the (writable , readable) for fields in register form
        self.register_visibility = {
                              "nickname": (True, True)
                              }

        # it sets the (writable , readable) for fields in profile form
        self.profile_visibility = {
                              "nickname": (True, True),
                              "website": (True, True),
                              "avatar": (True, True),
                              "thumbnail": (True, True),
                              "about": (True, True),
                              "gender": (True, True),
                              "birthdate": (True, True),
                             }

        self.computations = {
          "thumbnail": lambda r: THUMBER(r['avatar']),
        }

        self.labels = {
          "first_name": T("First Name"),
          "last_name": T("Last Name"),
          "email": T("E-mail"),
          "password": T("Password"),
          "nickname": T("Username"),
          "website": T("website"),
          "avatar": T("avatar"),
          "about": T("about"),
          "gender": T("Gender"),
          "birthdate": T("Birth Date"),
        }

        self.comments = {
          "nickname": T("Your desired username"),
          "website": T("website or blog"),
          "avatar": T("your profile picture"),
          "about": T("about you"),
          "gender": T("Gender"),
          "birthdate": T("Birth Date"),
        }

        self.validators = {
          "nickname": IS_NOT_EMPTY()
        }
