# Custom Authentication Class
# Implementation similar to gluon.tools

import hashlib


from gluon.html import URL
from gluon.http import redirect

# Authentication in pyForum will work in the following way:
#
# 3rd. Party Authentication Provider
# ----------------------------------
# This method will utilize a 3rd. party authenticator, upon successful
# authentication, the system will do one of the following:
# 1) If the user already exists, the system will log the user in, no
#    other update will be performed.
# 2) If the user does not exist in the system, the system will create a brand
#    new user and profile for the user, the 'password' of this user's profile
#    will be set to a 'fake' or pseudo-random hash, since pyForum will never
#    collect sensitive information from its users (nor it can under this
#    scenario anyway).
# Local User Account
# ------------------
# pyForum is capable of creating 'local' user accounts that do not depend on
# any external sources (FaceBook, Google, etc), the account is protected with
# a hash containing the user's username (not email), and the actual password
#
# What does all this mean? - it basically mean that you may sign up as a user
# with your google account, and once logged in, go and change your password,
# this will effectively make you a "local" account and you may 'skip' the
# registration process, pretty slick huh?. It also has the side effect of
# having an account that you can sign in with your pyForum-only password *or*
# with your google account (without pyForum even knowing the google's pwd of
# curse, man I'm _good_ :)


class CustomAuthentication(object):
    """ Role-Based authentication module """

    def __init__(self, environment, db):
        self.request = environment['request']
        self.response = environment['response']
        self.session = environment['session']
        self.cache = environment['cache']
        self.T = environment['T']
        self.db = db
        self._anonymous_user = 'Anonymous User'
        self.environment = environment
        self.__user_id = None

    def __call__(self):
        """ Returns the username (email) """
        return self.session.auth_email or self._anonymous_user

    def authenticate(self, auth_email, auth_passwd):
        """ sets authentication for the user """
        self.logout()  # Clear up previous session if any
        hash_pwd = hashlib.sha1('%s%s' % (auth_email, auth_passwd)).hexdigest()
        rows = self.db((self.db.auth_users.auth_email == auth_email) &
            (self.db.auth_users.auth_passwd == hash_pwd) &
            (self.db.auth_users.is_enabled == True)).select()
        if rows:
            self.__user_id = rows[0].id
            # These two next values go into our session
            self.session.auth_email = auth_email
            self.session.user_id = self.__user_id
            auth = True
        return self.session.user_id

    def authenticate_janrain(self, identifier, name, email, profile_pic_url):
        """ Authenticates against JANRAIN, formerly RPX, an authentication
        provider, see http://janrain.com/ for more information


        """
        # Note: If this method is called, it means that the user
        # has been authenticated by the external source (janrain)
        # So all is left to be done is to add the user to our user DB
        # if he/she does not exist, and (*or*, if the user does indeed already
        # exist) update the user's metadata...
        # (name, email)
        # In addition, I am not (currently doing anything with profile_pic_url
        # or identifier but they might come in handy later.
        self.logout()  # Clear up previous session if any
        user = self.db(
            (self.db.auth_users.auth_email == email) &
            (self.db.auth_users.is_enabled == True)).select().first()
        if user is None:
            # User does not exist, create it
            # This password is fake, not used for anything really...
            hash_passwd = hashlib.sha1('%s%s' % (name, identifier)).hexdigest()
            # New User - add it with the default role of Member
            # NOTE: THIS ROLE MUST EXIST
            auth_role_id = self.db(
                self.db.auth_roles.auth_role_name == 'zMember').select(
                    self.db.auth_roles.id)[0].id
            auth_user_id = self.db.auth_users.insert(
                auth_email=email,
                auth_passwd=hash_passwd,
                auth_created_on=self.request.now,
                auth_modified_on=self.request.now,
                is_enabled=True)

            # Also, add this user's default role to the corresponding table.
            self.db.auth_user_role.insert(auth_user_id=auth_user_id,
                                          auth_role_id=auth_role_id)
            # Read the (new) user's back
            user = self.db(
                (self.db.auth_users.auth_email == email) &
                (self.db.auth_users.is_enabled == True)).select().first()
        user_id = user.id  # Convenience
        self.__user_id = user_id
        self.session.auth_email = email
        self.session.user_id = user_id
        return user_id

    def logout(self):
        """ Clear the session """
        self.session.auth_email = None
        self.session.user_id = None

    def has_role(self, roles):
        """ Receives a comma-separated string containing the roles to check
        and will return True if the user contains any of the passed roles

        """
        hasrole = False
        roles_to_check = roles.split(',')
        roles_found = []
        if self.is_auth():
            auth_email = self.session.auth_email
            # select
            #   ar.auth_role_name
            # from
            #   auth_roles as ar,
            #   auth_user_role as aur,
            #   auth_users as au
            # where
            #   au.auth_email = %(auth_email)s
            #   and au.id = aur.auth_user_id
            #   and aur.auth_role_id = ar.id
            user_roles = self.db(
                (self.db.auth_users.auth_email == auth_email) &\
                (self.db.auth_users.id == \
                 self.db.auth_user_role.auth_user_id) &\
                (self.db.auth_user_role.auth_role_id == \
                 self.db.auth_roles.id)).select(
                self.db.auth_roles.auth_role_name)
            if user_roles:
                roles_found = [each_role for each_role in user_roles
                               if each_role.auth_role_name in roles_to_check]
                if roles_found:
                    hasrole = True
        return hasrole

    def get_roles(self):
        """ Returns a list of roles the user belongs to """
        roles = []
        if self.is_auth():
            auth_email = self.get_user_name()
            user_roles = self.db(
                (self.db.auth_users.auth_email == auth_email) &\
                (self.db.auth_users.id == \
                 self.db.auth_user_role.auth_user_id) &\
                (self.db.auth_user_role.auth_role_id == \
                 self.db.auth_roles.id)).select(
                self.db.auth_roles.auth_role_name)
            if user_roles:
                roles = [each_role.auth_role_name for each_role in user_roles]
        return roles

    def get_user_id(self):
        """ Returns the ID (Numeric) for the authentcated user, or None (NULL)
        if the user is not authenticated in the system

        """
        return self.session.user_id

    def get_user_name(self):
        """ same as __call__ - returns the 'username' (email) """
        return self.session.auth_email or self._anonymous_user

    def get_user_email(self):
        """ Deprecated - for compatibility only, use get_user_name()
        instead

        """
        return self.get_user_name()

    def is_auth(self):
        """ True if the user has been authenticated in the system,
        false otherwise

        """
        return True if self.session.user_id is not None else False

    def is_admin(self):
        """ This is a hack-y method (or shortcut) that can become useful in
        the future if the developer decides that "zAdministrator" should
        not be the only "admin" in the system

        """
        return self.has_role('zAdministrator')

    def requires_login(self):
        """ Decorator Helper to aid in determine whether a controller needs
        specific access

        """
        def wrapper(func):

            def f(*args, **kwargs):
                if not self.is_auth():
                    return redirect(URL(r=self.request, c='default',
                                        f='login'))
                return func(*args, **kwargs)

            return f

        return wrapper

    def requires_role(self, roles):
        """ Decorator Helper to aid in determine whether a controller needs
        specific access

        """
        def wrapper(func):

            def f(*args, **kwargs):
                if not self.has_role(roles):
                    return redirect(URL(r=self.request, c='default',
                                        f='login'))
                return func(*args, **kwargs)

            return f

        return wrapper
