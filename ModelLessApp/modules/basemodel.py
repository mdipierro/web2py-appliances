# -*- coding: utf-8 -*-

###############################################################################
# web2py modelless scaffold app
# Bruno Cezar Rocha <rochacbruno@gmail.com>
#
# This is the super class for all datamodels
# fields and its properties are created here
###############################################################################

from gluon.dal import DAL
from gluon.tools import Auth


class BaseModel(object):
    """Base Model Class
    all define_ methods will be called, then
    all set_ methods (hooks) will be called."""

    hooks = ['set_table',
             'set_validators',
             'set_visibility',
             'set_representation',
             'set_widgets',
             'set_labels',
             'set_comments',
             'set_computations',
             'set_updates',
             'set_fixtures']

    def __init__(self, db=None, migrate=None, format=None):
        self.db = db
        assert isinstance(self.db, DAL)
        self.config = db.config
        if migrate != None:
            self.migrate = migrate
        elif not hasattr(self, 'migrate'):
            self.migrate = self.config.db.migrate
        if format != None or not hasattr(self, 'format'):
            self.format = format
        self.set_properties()
        self.check_properties()
        self.define_table()
        self.define_validators()
        self.define_visibility()
        self.define_representation()
        self.define_widgets()
        self.define_labels()
        self.define_comments()
        self.define_computations()
        self.define_updates()
        self.pre_load()

    def check_properties(self):
        pass

    def define_table(self):
        fakeauth = Auth(DAL(None))
        self.fields.extend([fakeauth.signature])
        self.entity = self.db.define_table(self.tablename,
                                           *self.fields,
                                           **dict(migrate=self.migrate,
                                           format=self.format))

    def define_validators(self):
        validators = self.validators if hasattr(self, 'validators') else {}
        for field, value in validators.items():
            self.entity[field].requires = value

    def define_visibility(self):
        try:
            self.entity.is_active.writable = self.entity.is_active.readable = False
        except:
            pass
        visibility = self.visibility if hasattr(self, 'visibility') else {}
        for field, value in visibility.items():
            self.entity[field].writable, self.entity[field].readable = value

    def define_representation(self):
        representation = self.representation if hasattr(self, 'representation') else {}
        for field, value in representation.items():
            self.entity[field].represent = value

    def define_widgets(self):
        widgets = self.widgets if hasattr(self, 'widgets') else {}
        for field, value in widgets.items():
            self.entity[field].widget = value

    def define_labels(self):
        labels = self.labels if hasattr(self, 'labels') else {}
        for field, value in labels.items():
            self.entity[field].label = value

    def define_comments(self):
        comments = self.comments if hasattr(self, 'comments') else {}
        for field, value in comments.items():
            self.entity[field].comment = value

    def define_computations(self):
        computations = self.computations if hasattr(self, 'computations') else {}
        for field, value in computations.items():
            self.entity[field].compute = value

    def define_updates(self):
        updates = self.updates if hasattr(self, 'updates') else {}
        for field, value in updates.items():
            self.entity[field].update = value

    def pre_load(self):
        for method in self.hooks:
            if hasattr(self, method):
                self.__getattribute__(method)()


class BaseAuth(BaseModel):
    def __init__(self, auth, migrate=None):
        self.auth = auth
        assert isinstance(self.auth, Auth)
        self.db = auth.db
        from gluon import current
        self.request = current.request
        self.config = self.db.config
        self.migrate = migrate or self.config.db.migrate
        self.set_properties()
        self.define_extra_fields()
        self.auth.define_tables(migrate=self.migrate)
        self.entity = self.auth.settings.table_user
        self.define_validators()
        self.hide_all()
        self.define_visibility()
        self.define_register_visibility()
        self.define_profile_visibility()
        self.define_representation()
        self.define_widgets()
        self.define_labels()
        self.define_comments()
        self.define_computations()
        self.define_updates()
        self.pre_load()

    def define_extra_fields(self):
        self.auth.settings.extra_fields['auth_user'] = self.fields

    def hide_all(self):
        alwaysvisible = ['first_name', 'last_name', 'password', 'email']
        for field in self.entity.fields:
            if not field in alwaysvisible:
                self.entity[field].writable = self.entity[field].readable = False

    def define_register_visibility(self):
        if 'register' in self.request.args:
            register_visibility = self.register_visibility if hasattr(self, 'register_visibility') else {}
            for field, value in register_visibility.items():
                self.entity[field].writable, self.entity[field].readable = value

    def define_profile_visibility(self):
        if 'profile' in self.request.args:
            profile_visibility = self.profile_visibility if hasattr(self, 'profile_visibility') else {}
            for field, value in profile_visibility.items():
                self.entity[field].writable, self.entity[field].readable = value
