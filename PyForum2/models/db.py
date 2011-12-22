#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import sys
import os

# Adds our "Modules" folder to our environment path
path = os.path.join(request.folder, 'modules')
if not path in sys.path:
    sys.path.append(path)

from gluon.tools import *
from forumhelper import ForumHelper
from auth import CustomAuthentication

# Control Migrations
migrate = True # False if DB Schema already exists (? - Read Docs Pls)
fake_migrate = False # True to regen table info for EXISTING tables (run once)

#db=DAL("mysql://web2py:py2web@localhost:3306/pyforum")
db = DAL('sqlite://pyforum.sqlite', migrate=migrate)

 # Instantiate Authentication
auth_user = CustomAuthentication(globals(), db)
# Make Systemwide methods available
forumhelper = ForumHelper(globals(), db, auth_user)

## Authentication Schema (3 tables)
db.define_table('auth_users',
                db.Field('auth_email', 'string', length=128, required=True),
                db.Field('auth_passwd', 'string', length=128, required=True),
                db.Field('auth_created_on', 'string', required=True),
                db.Field('auth_modified_on', 'string', required=True),
                db.Field('is_enabled', 'boolean', required=False,
                         default=True),
                migrate='auth_users.table', fake_migrate=fake_migrate)

# Roles: Manager, Approver, Reviewer, etc
db.define_table('auth_roles',
                db.Field('auth_role_name',
                         'string', length=128, required=True),
                migrate='auth_roles.table', fake_migrate=fake_migrate)

# User/Role Mapping
db.define_table('auth_user_role',
                db.Field('auth_user_id', db.auth_users),
                db.Field('auth_role_id', db.auth_roles),
                migrate='auth_user_role.table', fake_migrate=fake_migrate)

# zf_forum_category
# Categories just provide a "container" for each discussion board (zf_forum).
# cat_desc is optional and it may be used to provide a longer description of
# the category
# cat_public is a flag that determines if an anonymous user can view the forum
# cat_visible_to controls the roles for which the category be available for
# viewing
db.define_table('zf_forum_category',
                db.Field('cat_name', 'string', length=255, required=True),
                db.Field('cat_desc', 'text', default=''),
                db.Field('cat_visible_to', 'string',
                         length=255, required=True),
                db.Field('cat_sort', 'integer', required=False, default=0),
                migrate='zf_forum_category.table', fake_migrate=fake_migrate)

# zf_forum
# This is the topics container and in itself it a containee of a category
db.define_table('zf_forum',
                db.Field('cat_id', db.zf_forum_category),
                db.Field('forum_title', 'string', length=255, required=True),
                db.Field('forum_desc', 'text', default=''),
                db.Field('moderation_flag', 'boolean', required=True,
                         default=False),
                db.Field('anonymous_viewaccess', 'boolean', required=False,
                         default=True),
                db.Field('add_postings_access_roles', 'string', length=255,
                         default=''),
                db.Field('reply_postings_access_roles', 'string', length=255,
                         default=''),
                db.Field('include_latest_topics', 'boolean', required=False,
                         default=True),
                db.Field('forum_sort', 'integer', required=False, default=0),
                migrate='zf_forum.table', fake_migrate=fake_migrate) 

# zf_topic
# This is the actual topic, it depends exclusively on zf_forum
db.define_table('zf_topic',
                db.Field('forum_id', db.zf_forum),
                db.Field('title', 'string', length=255, required=True),
                db.Field('content', 'text', required=True),
                db.Field('parent_id', 'integer', required=False, default=0),
                db.Field('creation_user_id', 'integer', required=False,
                         default=0),
                db.Field('creation_date', 'datetime', required=True),
                db.Field('modifying_user_id', 'integer', required=False,
                         default=0),
                db.Field('modifying_date', 'datetime', required=True),
                db.Field('hits', 'integer', required=False, default=0),
                db.Field('parent_flag', 'boolean', required=False),
                db.Field('locked_flag', 'boolean', required=False),
                db.Field('disabled_flag', 'boolean', required=False),
                db.Field('sticky_flag', 'boolean', required=False),
                db.Field('poll_flag', 'boolean', required=False),
                db.Field('system_announcement_flag', 'boolean',
                         required=False),
                db.Field('reply_to_topic_id', 'integer', required=False,
                         default=0),
                db.Field('ip_address', 'string', required=True),
                # !NEW CODE: profile_flag:
                #     This field indicates whether the topic should be hidden
                #     in a profile. This is only relevant for profile-specific topics.
                db.Field('profile_hidden', 'boolean', required=False, default=False),
                # !END NEW CODE
                migrate='zf_topic.table', fake_migrate=fake_migrate)

# !NEW TABLE: zf_referenced_topic:
#     This table defines the existing topics a user has linked to their profile.
#     Any thread linked in this way can be accessed via their profile page.
db.define_table('zf_referenced_topic',
                db.Field('topic_id', db.zf_topic),
                db.Field('user_id', db.auth_users),
                db.Field('profile_hidden', 'boolean', required=False, default=False),
                migrate='zf_referenced_topic.table', fake_migrate=fake_migrate)
# !END NEW TABLE

# !NEW TABLE: zf_friend_user
#     This holds a one-way friend relationship between self_id and a target user id.
db.define_table('zf_friend_user',
                db.Field('self_id', db.auth_users),
                db.Field('target_id', db.auth_users),
                migrate='zf_friend_user.table', fake_migrate=fake_migrate) 
# !END NEW TABLE

# System Support Tables

# System Properties - Used by the system itself
db.define_table('zf_system_properties',
                db.Field('property_name', 'string', length=128, required=True),
                db.Field('property_desc', 'text', required=True),
                db.Field('property_value', 'text', required=True),
                migrate='zf_system_properties.table',
                fake_migrate=fake_migrate)

# Member Properties (Skeleton) (Available member Properties)
db.define_table('zf_member_properties_skel',
                db.Field('property_name', 'string', length=128, required=True),
                db.Field('property_desc', 'text', required=True),
                db.Field('member_editable', 'boolean', default=False),
                migrate='zf_member_properties_skel.table',
                fake_migrate=fake_migrate)

# Member Properties (For each member)
db.define_table('zf_member_properties',
                db.Field('user_id', db.auth_users),
                db.Field('property_id', db.zf_member_properties_skel),
                db.Field('property_value', 'string', length=255,
                         required=True),
                # !NEW CODE: publicly_visible:
                #     This field determines whether the field is visible in a user's 
                #     public profile
                db.Field('profile_hidden', 'boolean', required=False, default=False),
                # !END NEW CODE
                migrate='zf_member_properties.table',
                fake_migrate=fake_migrate)

# Avatars
db.define_table('zf_member_avatars',
                db.Field('content_type', 'string', length=128, required=True),
                db.Field('user_id', db.auth_users),
                db.Field('avatar_image', 'blob', required=True, default=None),
                db.Field('avatar_active', 'boolean', required=True,
                         default=True),
                migrate='zf_member_avatars.table', fake_migrate=fake_migrate)

# Member Subscriptions (subscription_type =  ENUM('f', 't') --> Forum or Topic
db.define_table('zf_member_subscriptions',
                db.Field('user_id', db.auth_users),
                db.Field('subscription_id', 'integer', required=True,
                         default=0),
                db.Field('subscription_type', 'string', required=True),
                db.Field('subscription_active', 'boolean', default=True,
                         required=True),
                migrate='zf_member_subscriptions.table',
                fake_migrate=fake_migrate)

db.define_table('zf_member_subscriptions_notification',
                db.Field('user_id', db.auth_users),
                db.Field('subscription_id', 'integer', required=True,
                         default=0),
                db.Field('subscription_type', 'string', required=True),
                db.Field('creation_date', 'datetime', required=True),
                db.Field('is_processed', 'boolean', default=False,
                         required=True),
                migrate='zf_member_subscriptions_notification.table',
                fake_migrate=fake_migrate)

# Member Personal Messages
db.define_table('zf_pm_categories',
                db.Field('display_order', 'integer', required=True, default=0),
                db.Field('name', 'string', length=128, required=True),
                migrate='zf_pm_categories.table', fake_migrate=fake_migrate)

db.define_table('zf_pm',
                db.Field('cat_id', db.zf_pm_categories),
                db.Field('read_flag', 'boolean', default=False, required=True),
                db.Field('user_id', db.auth_users),
                db.Field('from_user_id', db.auth_users),
                db.Field('subject', 'string', length=255, required=True),
                db.Field('message', 'text', required=True),
                db.Field('creation_date', 'datetime', required=True),
                migrate='zf_pm.table', fake_migrate=fake_migrate)

db.define_table('zf_admin_messages',
                db.Field('user_id', 'integer', required=False, default=0),
                db.Field('subject', 'string', length=255, required=True),
                db.Field('message', 'text', required=True),
                db.Field('creation_date', 'datetime', required=True),
                db.Field('read_flag', 'boolean', default=False, required=True),
                migrate='zf_admin_messages.table', fake_migrate=fake_migrate)

db.define_table('zf_available_languages',
                db.Field('language_code', 'string', required=True, length=5),
                db.Field('language_desc', 'string', required=True, length=255),
                db.Field('enabled', 'boolean', required=True, default=True),
                migrate='zf_available_languages.table',
                fake_migrate=fake_migrate)

db.define_table('zf_member_rank',
                db.Field('rank_name', 'string', required=True, length=128),
                db.Field('rank_value_min', 'integer', required=True,
                         default=0),
                migrate='zf_member_rank.table', fake_migrate=fake_migrate)
                
db.define_table('zf_topic_inappropriate',
                db.Field('topic_id', db.zf_topic),
                db.Field('child_id', 'integer', required=True),
                db.Field('creation_user_id', 'string', required=True, length=255),
                db.Field('creation_date', 'datetime', required=True),
                db.Field('read_flag', 'boolean', default=False, required=True),
                migrate='zf_topic_inappropriate.table',
                fake_migrate=fake_migrate)

db.define_table('zf_member_banned',
                db.Field('user_id', db.auth_users),
                db.Field('ban_date', 'datetime', required=True),
                migrate='zf_member_banned.table', fake_migrate=fake_migrate)

db.define_table('zf_ip_banned',
                db.Field('ip', 'string', length=255, required=True),
                db.Field('ban_date', 'datetime', required=True),
                migrate='zf_ip_banned.table', fake_migrate=fake_migrate)

# Next, verify that the necessary table information exists in the system,
# otherwise create it
if not db(db.auth_roles.id > 0).count():
    data_list = []
    data_list.append({'auth_role_name': 'zAdministrator'})
    data_list.append({'auth_role_name': 'zMember'})
    # This role can be used to effectively have to member lists,
    # They can potentially share memberships
    data_list.append({'auth_role_name': 'zMemberVIP'})
    # !NEW CODE
    #     Added role zMemberMedia for embedded files 
    data_list.append({'auth_role_name': 'zMemberMedia'})
    db.auth_roles.bulk_insert(data_list)
    
if not db(db.zf_member_properties_skel.id > 0).count():
    data_list = []
    data_list.append({'property_name': 'zfmp_last_login',
                      'property_desc': 'Last Login',
                      'member_editable': False})
    data_list.append({'property_name': 'zfmp_last_login_ip',
                      'property_desc': 'Last Login IP',
                      'member_editable': False})
    data_list.append({'property_name': 'zfmp_allow_pm_use',
                      'property_desc': 'Allow be Contacted by Other Members',
                      'member_editable': True})
    data_list.append({'property_name': 'zfmp_postings',
                      'property_desc': 'Number of Postings',
                      'member_editable': False})
    data_list.append({'property_name': 'zfmp_locale',
                      'property_desc': 'Language for display',
                      'member_editable': True})
    data_list.append({'property_name': 'zfmp_signature',
                      'property_desc': 'Member Signature',
                      'member_editable': True})
    data_list.append({'property_name': 'zfmp_web_page',
                      'property_desc': 'Member URL',
                      'member_editable': True})
    data_list.append({'property_name': 'zfmp_country',
                      'property_desc': 'Member City/Country',
                      'member_editable': True})
    data_list.append({'property_name': 'zfmp_join_date',
                      'property_desc': 'Join Date',
                      'member_editable': False})
    data_list.append({'property_name': 'zfmp_real_name',
                      'property_desc': 'Member Full Name',
                      'member_editable': True})
    data_list.append({'property_name': 'zfmp_display_name',
                      'property_desc': 'Display Name in the Forum System',
                      'member_editable': True})
    # !NEW CODE
    #     Additional member properties to be created by default for system
    data_list.append({'property_name': 'zfmp_user_info',
                      'property_desc': 'User Info',
                      'member_editable': True})
    # !END NEW CODE
    db.zf_member_properties_skel.bulk_insert(data_list)

if not db(db.zf_system_properties.id > 0).count():
    data_list = []
    data_list.append({'property_name': 'zfsp_threads_per_page',
                      'property_desc': 'Threads per Page: Number of results '
                      'per page to show in the topic display section',
                      'property_value': '20'})
    data_list.append({'property_name': 'zfsp_email_pwd_on_signup',
                      'property_desc': 'Email Password Upon Signup: Regadless '
                      'of what signup method is used, the new user will '
                      'receive a welcome email',
                      'property_value': ''})
    data_list.append({'property_name': 'zfsp_topic_teaser_length',
                      'property_desc': 'Topic Teaser Length: The number of '
                      'characters shown for a topic when it is viewed from '
                      'the ""view forum"" page, a value of 0 or an empty '
                      'value disables this option, a suggested value would '
                      'be 250 characters',
                      'property_value': '250'})
    data_list.append({'property_name': 'zfsp_allow_member_avatars',
                      'property_desc': 'Allow Avatars: If empty, users will '
                      'not be given the choice of adding or change their '
                      'avatars, any other value will enable avatars for '
                      'all registered users in the system',
                      'property_value': 'True'})
    data_list.append({'property_name': 'zfsp_system_language',
                      'property_desc': 'System Language: Selects the default '
                      'system language, if invalid it will default to '
                      'English (US)',
                      'property_value': 'en'})
    data_list.append({'property_name': 'zfsp_admin_contact_email',
                      'property_desc': 'Admin Contact: (Important) - The '
                      'forum system uses this value to specify the *From* '
                      'email header for any email that is sent out, please '
                      'use a valid email address that your domain will '
                      'recognize, otherwise your system may not send emails '
                      'at all',
                      'property_value': ''})
    data_list.append({'property_name': 'zfsp_mailserver',
                      'property_desc': 'Mail Server: The mail server to use '
                      'when sending out emails',
                      'property_value': 'localhost'})
    data_list.append({'property_name': 'zfsp_mailserver_username',
                      'property_desc': 'Mail Server: The username to use if '
                      'authenticating against a mail server',
                      'property_value': ''})
    data_list.append({'property_name': 'zfsp_mailserver_passwd',
                      'property_desc': 'Mail Server:  The password to use '
                      'if authenticating against a mail server',
                      'property_value': ''})
    data_list.append({'property_name': 'zfsp_use_ranking_system',
                      'property_desc': 'Use Ranking System: If enabled, the '
                      'system will use its internal ranking system, if empty '
                      'the system will not use a ranking system at all',
                      'property_value': 'True'})
    data_list.append({'property_name': 'zfsp_hot_topic_threshold',
                      'property_desc': 'Hot Topic Threshold: Number of views '
                      'necessary to mark the topic as *hot*',
                      'property_value': '50'})
    data_list.append({'property_name': 'zfsp_member_quota',
                      'property_desc': 'Message Quota: Leave empty to disable '
                      'quotas for messages for your users, any other numeric '
                      'value will represent the number of bytes of allowance, '
                      'an invalid amount will always default to 50Kb per user',
                      'property_value': '50000'})
    data_list.append({'property_name': 'zfsp_system_announcement_max',
                      'property_desc': 'System Announcements View: This '
                      'controls the (maximum) number of system announcements '
                      'that pyForum will display in its right nav, an invalid '
                      'value or zero will show a =-No System Messages-= title',
                      'property_value': '5'})
    data_list.append({'property_name': 'zfsp_latest_postings_max',
                      'property_desc': 'Latest Postings View: This controls '
                      'the (maximum) number of latest postings that pyForum '
                      'will display in its right nav, an invalid value or '
                      'zero will show a =-No Messages-= title',
                      'property_value': '5'})
    data_list.append({'property_name': 'zfsp_responses_per_page',
                      'property_desc': 'Responses per page: Controls the '
                      'amount of responses (children topics) that pyForum '
                      'will show and will add pagination accordingly',
                      'property_value': '15'})
    data_list.append({'property_name': 'zfsp_header_html',
                      'property_desc': 'Header Text: This can contain html '
                      'code and will be shown at the top-right corner of '
                      'pyForum',
                      'property_value': 'Welcome to pyForum'})
    data_list.append({'property_name': 'zfsp_allow_registration',
                      'property_desc': 'Allows User self-registration. Any '
                      'value will allow a member to self-register in the '
                      'forum system, an empty value disables this option',
                      'property_value': 'True'})
    db.zf_system_properties.bulk_insert(data_list)
    
if not db(db.zf_pm_categories.id).count():
    data_list = []
    data_list.append({'name': 'Inbox',
                      'display_order': 1})
    data_list.append({'name': 'Read',
                      'display_order': 2})
    data_list.append({'name': 'Sent',
                      'display_order': 3})
    data_list.append({'name': 'Trash',
                      'display_order': 4})
    db.zf_pm_categories.bulk_insert(data_list)

# !NEW CODE
#     This adds the Administration category and Profile forum to the system
#     if they are not already present. 
if not db(db.zf_forum_category.id).count():
    new_cat_name = "Administration"
    new_cat_visible_to = "zAdministrator"
    new_cat_desc = "This category is only visible to admins."
    db.zf_forum_category.insert(cat_name=new_cat_name, cat_visible_to=new_cat_visible_to, cat_desc=new_cat_desc)
    if not db(db.zf_forum.id).count():
        new_cat_id = db(db.zf_forum_category.cat_name==new_cat_name).select(db.zf_forum_category.id)[0]
        new_forum_title = "Profile"
        new_forum_desc = "This forum holds topics created by a user in their own profile. It is only publicly visible to non-admins in their profile."
        new_moderation_flag = True
        new_anonymous_viewaccess = False
        new_add_postings_access_roles = "Authenticated"
        new_reply_postings_access_roles = "Authenticated"
        new_include_latest_topics = False
        new_forum_sort = 0
        db.zf_forum.insert(cat_id=new_cat_id, forum_title=new_forum_title, forum_desc=new_forum_desc, moderation_flag=new_moderation_flag, anonymous_viewaccess=new_anonymous_viewaccess, add_postings_access_roles = new_add_postings_access_roles, reply_postings_access_roles=new_reply_postings_access_roles, include_latest_topics = new_include_latest_topics, forum_sort=new_forum_sort)
# !END NEW CODE        

if not db(db.zf_member_rank.id > 0).count():
    data_list = []
    data_list.append({'rank_value_min': 0,
                      'rank_name': 'Rank 1'})
    data_list.append({'rank_value_min': 30,
                      'rank_name': 'Rank 2'})
    data_list.append({'rank_value_min': 50,
                      'rank_name': 'Rank 3'})
    data_list.append({'rank_value_min': 100,
                      'rank_name': 'Rank 4'})
    data_list.append({'rank_value_min': 250,
                      'rank_name': 'Rank 5'})
    data_list.append({'rank_value_min': 400,
                      'rank_name': 'Rank 6'})
    data_list.append({'rank_value_min': 500,
                      'rank_name': 'Rank 7'})
    data_list.append({'rank_value_min': 800,
                      'rank_name': 'Rank 8'})
    data_list.append({'rank_value_min': 1000,
                      'rank_name': 'Rank 9'})
    data_list.append({'rank_value_min': 2000,
                      'rank_name': 'Rank 10'})
    data_list.append({'rank_value_min': 3000,
                      'rank_name': 'Rank 11'})
    db.zf_member_rank.bulk_insert(data_list)

if not db(db.auth_users.id > 0).count():
    temp_email = 'administrator@pyforum.org'
    temp_passwd = forumhelper.gen_pwd()
    # New User - add it with the default role of Member
    # NOTE: THIS ROLE MUST EXIST
    auth_role_id = db(
        db.auth_roles.auth_role_name=='zAdministrator').select(
        db.auth_roles.id)[0].id
    auth_user_id = db.auth_users.insert(
        auth_email=temp_email,
        auth_passwd=hashlib.sha1(temp_email + temp_passwd).hexdigest(),
        auth_created_on=request.now,
        auth_modified_on=request.now,
        is_enabled=True)    
    # Also, add this user's default role to the corresponding table.
    db.auth_user_role.insert(auth_user_id=auth_user_id,
                             auth_role_id=auth_role_id)
    # Stuff this info into the session, a bit of magic here since web2py
    # "provides" us with a session object in our environment
    session.RUN_ONCE = 1
    session.NEW_USER = temp_email
    session.NEW_USER_PASSWD = temp_passwd
