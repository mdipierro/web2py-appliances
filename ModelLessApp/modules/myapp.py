# -*- coding: utf-8 -*-

###############################################################################
# web2py modelless scaffold app
# Bruno Cezar Rocha <rochacbruno@gmail.com>
#
# This is the base of the app
# it acts like a proxy for the rest of the application
#
# Why subclassing Auth, DAL, Mail etc?
# 1. Because you can reuse the code better
# 2. Because you can have self configured instances ready to use
# 3. Because it is a way to change or replace some default behaviour when needed
#
###############################################################################

from gluon.tools import Auth, Crud, Mail
from gluon.dal import DAL
from datamodel.user import User
from gluon.storage import Storage
from gluon import current


class MyApp(object):
    def __init__(self):
        self.session, self.request, self.response, self.T = \
            current.session, current.request, current.response, current.T
        self.config = Storage(db=Storage(),
                              auth=Storage(),
                              crud=Storage(),
                              mail=Storage())
        # Global app configs
        # here you can choose to load and parse your configs
        # from JSON, XML, INI or db
        # Also you can put configs in a cache
        #### -- LOADING CONFIGS -- ####
        self.config.db.uri = "sqlite://myapp.sqlite"
        self.config.db.migrate = True
        self.config.db.migrate_enabled = True
        self.config.db.check_reserved = ['all']
        self.config.auth.server = "default"
        self.config.auth.formstyle = "divs"
        self.config.mail.server = "logging"
        self.config.mail.sender = "me@mydomain.com"
        self.config.mail.login = "me:1234"
        self.config.crud.formstyle = "divs"
        #### -- CONFIGS LOADED -- ####

    def db(self, datamodels=None):
        # here we need to avoid redefinition of db
        # and allow the inclusion of new entities
        if not hasattr(self, "_db"):
            self._db = DataBase(self.config, datamodels)
        if datamodels:
            self._db.define_datamodels(datamodels)
        return self._db

    @property
    def auth(self):
        # avoid redefinition of Auth
        # here you can also include logic to del
        # with facebook based in session, request, response
        if not hasattr(self, "_auth"):
            self._auth = Account(self.db())
        return self._auth

    @property
    def crud(self):
        # avoid redefinition of Crud
        if not hasattr(self, "_crud"):
            self._crud = FormCreator(self.db())
        return self._crud

    @property
    def mail(self):
        # avoid redefinition of Mail
        if not hasattr(self, "_mail"):
            self._mail = Mailer(self.config)
        return self._mail


class DataBase(DAL):
    """
    Subclass of DAL
    auto configured based in config Storage object
    auto instantiate datamodels
    """
    def __init__(self, config, datamodels=None):
        self.config = config
        DAL.__init__(self,
                     **config.db)

        if datamodels:
            self.define_datamodels(datamodels)

    def define_datamodels(self, datamodels):
        # Datamodels will define tables
        # datamodel ClassName becomes db attribute
        # so you can do
        # db.MyEntity.insert(**values)
        # db.MyEntity(value="some")
        for datamodel in datamodels:
            obj = datamodel(self)
            self.__setattr__(datamodel.__name__, obj.entity)
            if obj.__class__.__name__ == "Account":
                self.__setattr__("auth", obj)


class Account(Auth):
    """Auto configured Auth"""
    def __init__(self, db):
        self.db = db
        self.hmac_key = Auth.get_or_create_key()
        Auth.__init__(self, self.db, hmac_key=self.hmac_key)
        user = User(self)
        self.entity = user.entity

        # READ AUTH CONFIGURATION FROM CONFIG
        self.settings.formstyle = self.db.config.auth.formstyle
        if self.db.config.auth.server == "default":
            self.settings.mailer = Mailer(self.db.config)
        else:
            self.settings.mailer.server = self.db.config.auth.server
            self.settings.mailer.sender = self.db.config.auth.sender
            self.settings.mailer.login = self.db.config.auth.login


class Mailer(Mail):
    def __init__(self, config):
        Mail.__init__(self)
        self.settings.server = config.mail.server
        self.settings.sender = config.mail.sender
        self.settings.login = config.mail.login


class FormCreator(Crud):
    def __init__(self, db):
        Crud.__init__(db)
        self.settings.auth = None
        self.settings.formstyle = self.db.config.crud.formstyle
