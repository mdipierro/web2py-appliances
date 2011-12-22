import datetime
import hashlib
import base64
import urllib2
import urllib
import json

#from gluon.tools import prettydate

# IDE "helper" not part of the framework
if False:
    from gluon.globals import *
    from gluon.html import *
    from gluon.http import *
    #from gluon.sqlhtml import SQLFORM, SQLTABLE, form_factory
    session = Session()
    request = Request()
    response = Response()
    # The following three lines are application-specific and used just so
    # komodo (edit) (or even other IDEs sich as Wing) "finds" the methods
    # for my classes, this does not have anyhing to do with the web2py
    # framework itself, as I am already instantiating "auth_user",
    # "stackhelper, forumhelper" etc in one of my models...
    from pyforum.modules.auth import CustomAuthentication as auth_user
    from pyforum.modules.forumhelper import ForumHelper as forumhelper

def index():
    if session.RUN_ONCE is None:
        cat_list = []
        cat_dict = {}
        view_info = {}
        # Get all available Categories/Forums/Hits, etc, etc in one single,
        # optimized query and determine which ones the user is allowed to view.
        # This is one of the few SQL queries that I still need to port
        # to web2py's DAL, any takers?
        sql = """
        select
            zfc.id as cat_id,
            zfc.cat_name,
            zfc.cat_desc,
            zfc.cat_visible_to,
            zfc.cat_sort,
            zf.id as forum_id,
            zf.forum_title,
            zf.forum_desc,
            zf.moderation_flag,
            zf.anonymous_viewaccess,
            zf.add_postings_access_roles,
            zf.reply_postings_access_roles,
            zf.forum_sort,
            count(nullif(zt.parent_flag='T',0)) as parents,
            count(nullif(zt.parent_flag='F',0)) as siblings,
            sum(zt.hits) as hits
        from
            zf_forum_category as zfc
                left join zf_forum as zf on zfc.id = zf.cat_id
                left join zf_topic as zt on zt.forum_id = zf.id
                and zt.disabled_flag = 'F'
        group by
            zf.id,
            zf.forum_title,
            zf.forum_desc,
            zf.moderation_flag,
            zf.anonymous_viewaccess,
            zf.add_postings_access_roles,
            zfc.id,
            zfc.cat_name,
            zfc.cat_desc,
            zfc.cat_visible_to,
            zfc.cat_sort,
            zf.reply_postings_access_roles,
            zf.forum_sort
        order by
            zfc.cat_sort,
            zf.forum_sort
        """
        #raise ValueError(sql)
        # Returns a tuple and each tuple element containing the column values
        cats_and_forums = db.executesql(sql)
        if cats_and_forums:
            today = request.now
            now = datetime.datetime.now()
            for cat_forum in cats_and_forums:
                cat_id = cat_forum[0]
                cat_name = cat_forum[1]
                cat_desc = cat_forum[2]
                cat_visible_to_str = cat_forum[3]
                cat_sort = cat_forum[4]
                forum_id = cat_forum[5]
                forum_title = cat_forum[6]
                forum_desc = cat_forum[7]
                moderation_flag = cat_forum[8]
                anonymous_viewaccess = cat_forum[9]
                add_postings_access_roles = cat_forum[10]
                reply_postings_access_roles = cat_forum[11]
                forum_sort = cat_forum[12]
                parents = cat_forum[13]
                siblings = cat_forum[14]
                hits = cat_forum[15]

                cat_view_access = False

                cat_visible_to = cat_visible_to_str.strip().split(',')
                # Automatic access if the user is a forum admin, or if the
                # category itself is not restricted to noone (i.e. the
                # "cat_visible_to" field is empty (no roles):
                if auth_user.has_role(
                    'zAdministrator') or cat_visible_to_str.strip() == '':
                    cat_view_access = True
                
                # !NEW CODE:
                #     Additional elif statment added to quick fix bug in existing pyforum code.
                #     If authorized users are allowed to view a category, it is stored as 'Authenticated' in the db.
                #     The check whether to display those threads relies on the actual user roles, however,
                #     and there is no 'Authenticated' role. 
                elif cat_visible_to_str.find('Authenticated') != -1 and (auth_user.has_role('zMember') or auth_user.has_role('zMemberMedia') or auth_user.has_role('zMemberVIP')):
                    cat_view_access = True
                # !END NEW CODE
                
                else:
                    # The "key" here relies in the "auth_user.has_role(cat)"
                    cat_view_access = [
                        cat for cat in cat_visible_to
                        if auth_user.has_role(cat)] != []

                if cat_view_access:
                    if forum_id:
                        posts = 0
                        replies = 0
                        views = 0

                        if parents:
                            posts = parents
                        if siblings:
                            replies = siblings
                        if hits:
                            views = hits

                        # Get Forum Last Updated Data
                        #select
                        #    zft.modifying_user_if,
                        #    zft.modifying_date,
                        #    zft.topic_id,
                        #    zft.parent_flag,
                        #    zft.parent_id
                        #from
                        #    zf_topic as zft
                        #where
                        #    zft.forum_id = **forum_id**
                        #    and zft.disabled_flag = 0
                        #order by
                        #    zft.modifying_date desc
                        #limit 1
                        #offset 0
                        where_statement = (
                            db.zf_topic.forum_id == forum_id) & (
                            db.zf_topic.disabled_flag == 0)
                        last_update_info = db(
                            where_statement).select(
                            db.zf_topic.modifying_user_id,
                            db.zf_topic.modifying_date,
                            db.zf_topic.id,
                            db.zf_topic.parent_flag,
                            db.zf_topic.parent_id,
                            orderby=~db.zf_topic.modifying_date,
                            limitby=(0,1))
                        if last_update_info:
                            last_updated = last_update_info[0].modifying_date
                            last_updated_by = last_update_info[
                                0].modifying_user_id
                            if last_update_info[0].parent_flag:
                                last_updated_topic_id = last_update_info[0].id
                            else:
                                last_updated_topic_id = last_update_info[
                                    0].parent_id
                        else:
                            last_updated = None
                            last_updated_by = None
                            last_updated_topic_id = None

                        # Now, lets' set a flag to mark the "last updated"
                        # message in red (or any other visual cue) if the
                        # message is less than a day old (24 hs)
                        if last_updated:
                            # td is a timedelta object
                            td = (today - last_updated).days
                            if td == 0:
                                update_flag = True
                            else:
                                update_flag = False
                        else:
                            update_flag = False

                        # Now here is the deal, not everyone will be able
                        # to view/enter a particular forum, so here is when
                        # the logic applies. We'll check if the user logged
                        # in or not has the role needed note that a forum
                        # could have the role "Anonymous", which would give
                        # an anonymous user access to the forum's topics.
                        add_forum = False
                        access_roles = add_postings_access_roles.split(',') + \
                        reply_postings_access_roles.split(',')

                        if [role for role in access_roles \
                            if auth_user.has_role(role) or \
                            anonymous_viewaccess]:
                            add_forum = True

                        if add_forum:
                            if last_updated:
                                s_last_updated = last_updated.strftime(
                                    str(T('%b %d, %Y - %I:%M %p')))
                            else:
                                s_last_updated = ''
                            forum_dict = {'forum_id': forum_id,
                                          'forum_title': XML(forum_title),
                                          'forum_desc': forum_desc,
                                          'anonymous_viewaccess':
                                            anonymous_viewaccess,
                                          'posts': posts,
                                          'replies': replies,
                                          'views': views,
                                          'forum_sort': forum_sort,
                                          'last_updated': s_last_updated,
                                          'last_updated_by': last_updated_by,
                                          'last_updated_topic_id':
                                            last_updated_topic_id,
                                          'subscribed_to_forum':
                                            forumhelper.has_forum_subscription(
                                                forum_id,
                                                auth_user.get_user_id()),
                                          'update_flag': update_flag}
                            if cat_dict.has_key(cat_id):
                                cat_dict['forum_list'].append(forum_dict)
                            else:
                                cat_dict = {cat_id: cat_id,
                                            'cat_id': cat_id,
                                            'cat_name': cat_name,
                                            'cat_sort': cat_sort,
                                            'forum_list': [forum_dict],
                                            'cat_visible_to': cat_visible_to,
                                            'cat_desc': cat_desc}
                                cat_list.append(cat_dict)
                    else:
                        # Cat Visible but No Forums
                        cat_dict = {cat_id: cat_id,
                                    'cat_id': cat_id,
                                    'cat_name': cat_name,
                                    'cat_sort': cat_sort,
                                    'forum_list': [],
                                    'cat_visible_to': cat_visible_to,
                                    'cat_desc': cat_desc}
                        cat_list.append(cat_dict)
        # Here get the latest system announceemnt to display in the top line
        sys_topics = forumhelper.get_system_announcements(include_content=True)
        if len(sys_topics):
            sys_topic = sys_topics[0]
            if type(sys_topic) != type({}):
                view_info.update({'sys_topic': sys_topics[0]})

        return dict(cat_list=cat_list, view_info=view_info)
    else:
        # So apparently we have a new system install, redirect to the
        # appropriate page:
        redirect(URL(r=request, c='default', f='runonce'))


def runonce():
    """ This method will automatically be executed after initial install of
    the system.

    """
    if session.RUN_ONCE is not None:
        tmp_username = session['NEW_USER']
        tmp_passwd = session['NEW_USER_PASSWD']
        # Remove these values from the session now..
        session.RUN_ONCE = None
        session.NEW_USER_PASSWD = None
        session.RUN_ONCE = None
        return dict(tmp_username=tmp_username, tmp_passwd=tmp_passwd)
    else:
        # Just die silently..
        redirect(URL(r=request, c='default', f='index'))


def login():
    """ Handles login actions """
    custom_messages = {}
    errors = []
    isauth = False
    req = request.vars
    if req.form_submitted:
        if req.login_b:
            user_id = auth_user.authenticate(req.auth_alias, req.passwd)
            if user_id:
                # Now, update some properties
                forumhelper.put_member_property('zfmp_last_login', user_id,
                                                prettydate(request.now, T))
                isauth = True
            else:
                errors.append('Invalid Username or Password entered')
        else:
            redirect(URL(r=request, c='default', f='index'))
    custom_messages['errors'] = errors
    if isauth:
        # Grab the Language preferences here, and send it
        lang = forumhelper.get_member_property(
            property_name='zfmp_locale', user_id=user_id, default_value='')
        redirect(URL(r=request, c='default', f='index', vars=dict(lang=lang)))
    else:
        return dict(request=request, custom_messages=custom_messages)

def login_janrain():
    # Must be posted by the external calling process
    token = request.vars.token

    # Part of the Janrain API docs.
    api_params = {
    'token': token,
    'apiKey': '092eba675ac7eb1a3d6f82862984a2734c714829',
    'format': 'json',}

    # make the api call
    http_response = urllib2.urlopen('https://rpxnow.com/api/v2/auth_info',
                                urllib.urlencode(api_params))
    # read the json response
    auth_info_json = http_response.read()

    # Process the json response
    auth_info = json.loads(auth_info_json)
    # Step 4) use the response to sign the user in
    if auth_info['stat'] == 'ok':
        profile = auth_info['profile']

        # 'identifier' will always be in the payload
        # this is the unique identifier that you use to sign the user
        # in to your site
        identifier = profile['identifier']

        # These fields MAY be in the profile, but are not guaranteed. it
        # depends on the provider and their implementation.
        name = profile.get('displayName')
        email = profile.get('email')
        profile_pic_url = profile.get('photo')

        # Sign the user in.
        user_id = auth_user.authenticate_janrain(
            identifier,
            name.lower(),
            email.lower(),
            profile_pic_url)
        form_vars = {}

        # Now, update some properties
        forumhelper.put_member_property('zfmp_last_login', user_id,
                                        prettydate(request.now, T))
        # Only update Name (zfmp_display_name) if the field is actually empty
        # 'zfmp_display_name' is the name that the user will have in the
        # system, it is an editable property and it will show in various
        # parts of the system.
        if forumhelper.get_display_name(user_id, '') == '':
            forumhelper.put_member_property('zfmp_display_name', user_id,
                                            name)
    else:
        # TODO: Do something more elegant than this
        #raise ValueError('An error occured: %s' % (auth_info['err']['msg']))
        form_vars = dict(login_error=auth_info['err']['msg'])
    redirect(URL(r=request, c='default', f='index', vars=form_vars))


def logout():
    if session.has_key('lang'):
        del session['lang']
    auth_user.logout()
    redirect(URL(r=request, c='default', f='index', vars=dict(lang='')))

def view_forum():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    view_info['all_topics'] = 0
    security_info = {'can_add': False, 'can_reply': False}
    user_id = auth_user.get_user_id()

    if req.remove_topics:
        forum_id = (req.forum_id)
        forum = db(db.zf_forum.id==forum_id).select()[0]
    else:
        forum_id = int(request.args[0])
        # Here handle subscription/unsubscriptions
        if len(request.args) > 1 and auth_user.is_auth():
            subscription_flag = int(request.args[1])
            is_subscription = db(
                (db.zf_member_subscriptions.subscription_id == forum_id) &
                (db.zf_member_subscriptions.user_id==user_id)).select(
                db.zf_member_subscriptions.id)
            if subscription_flag == 1: # Request Subscription
                if len(is_subscription) == 0:
                    # (new) Subscription
                    db.zf_member_subscriptions.insert(
                        user_id=user_id,
                        subscription_id=forum_id,
                        subscription_type='F', subscription_active=True)
                else:
                    # Update an existing subscription back to "true"
                    db(
                        (db.zf_member_subscriptions.subscription_id == \
                         forum_id) &
                        (db.zf_member_subscriptions.subscription_type == 'F') &
                        (db.zf_member_subscriptions.user_id == \
                         user_id)).update(subscription_active=True)
            else: # User is requesting removal (or inactivate subscription)
                if len(is_subscription) > 0:
                    db(
                        (db.zf_member_subscriptions.subscription_id == \
                         forum_id) &
                        (db.zf_member_subscriptions.user_id == \
                         user_id)).update(subscription_active=False)
        forum = db(db.zf_forum.id==forum_id).select()[0]

    # Information to pass regarding system variables, etc
    # Forum Subscription:
    view_info.update({'subscribed_to_forum':
        forumhelper.has_forum_subscription(forum_id, user_id)})
    # Max preview length:
    view_info.update({'zfsp_topic_teaser_length':
        int(forumhelper.get_system_property('zfsp_topic_teaser_length', 250))})

    # Security Checks here
    user_can_enter = True
    if not auth_user.is_auth() and not forum.anonymous_viewaccess:
        user_can_enter = False

    if user_can_enter:
        if auth_user.is_admin():
            security_info['can_add'] = True
            security_info['can_reply'] = True
        else:
            if len(forum.add_postings_access_roles):
                security_info['can_add'] = [
                    role for role in auth_user.get_roles()
                    if forum.add_postings_access_roles.find(role)] != []
            else:
                security_info['can_add'] = True

            if len(forum.reply_postings_access_roles):
                security_info['can_reply'] = [
                    role for role in auth_user.get_roles()
                    if forum.reply_postings_access_roles.find(role)] != []
            else:
                security_info['can_reply'] = True

        if req.del_topics:
            for req_var in req:
                if req_var[:10] == 'del_topic_':
                    del_topic_id = int(req[req_var])
                    db(db.zf_topic.parent_id==del_topic_id).delete() # Children
                    db(db.zf_topic.id==del_topic_id).delete() # Parent
                    view_info.update({'topics_removed': True})


        # Pagination Manager Part I/II
        start = int(req.get('start', 0))
        #try:
        topics_per_page = int(
            forumhelper.get_system_property('zfsp_threads_per_page', 15))
        #except:
        #    topics_per_page = 15

        # all Topics
        all_topics = db((db.zf_topic.forum_id==forum_id) & \
            (db.zf_topic.parent_flag==True)).count()
        view_info['all_topics'] = all_topics
        parent_topics = db(
            (db.zf_topic.forum_id==forum_id) & \
            (db.zf_topic.parent_flag==True)).select(
            orderby=(~db.zf_topic.sticky_flag, ~db.zf_topic.modifying_date),
            limitby=(start, start+topics_per_page))

        # Pagination Manager Part II/II
        pagination_widget = forumhelper.pagination_widget(
            all_topics,
            start,
            URL(r=request, c='default', f='view_forum', args=[forum.id]),
            'forum')
        view_info.update({'pagination_widget': pagination_widget})

        # Now plug in the information regarding their children
        topic_replies_info = {}
        for topic in parent_topics:
            # Get the number of children topics for this (parent) topic
            topic_replies_info.update({topic.id:
                db(db.zf_topic.parent_id==topic.id).count()})
            # Topic Subscription
            if forumhelper.has_topic_subscription(topic.id, user_id):
                view_info.update({topic.id: {'subscribed_to_topic': True}})
            else:
                view_info.update({topic.id: {'subscribed_to_topic': False}})

        return dict(request=request, forum=forum, parent_topics=parent_topics,
                    view_info=view_info, security_info=security_info,
                    topic_replies_info=topic_replies_info)
    else:
        redirect(URL(r=request, c='default', f='unauthorized'))

def signup():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    captcha = forumhelper.gen_pwd()
    view_info['anon_captcha'] = captcha
    view_info['anon_captcha_base64'] = base64.standard_b64encode(captcha)
    allow_registration = forumhelper.get_system_property(
        'zfsp_allow_registration', '') != ''
    view_info.update({'allow_registration': allow_registration})
    if req.form_submitted:
        if req.register_b:

            # Verify required fields
            if len(req.auth_email) > 0 and len(req.auth_passwd) > 0:
                auth_email = req.auth_email.strip()
                auth_passwd = req.auth_passwd
                auth_passwd_c = req.auth_passwd_c

                # Lamo validation.. embarrasing ;)
                if auth_email.find(' ') >= 0:
                    view_info['errors'].append('Email must not contain spaces')

                if auth_passwd != auth_passwd_c:
                    view_info['errors'].append('Password and confirmation '
                                               'do not match')

                # See if this name has been taken
                if db(db.auth_users.auth_email.lower() == \
                      auth_email.lower()).select(db.auth_users.id):
                    view_info['errors'].append('The selected email is '
                                               'unavailable, please choose '
                                               'another one')
                if base64.standard_b64encode(req.captcha_response) != req.c:
                    view_info['errors'].append('Invalid humanity challenge '
                                               'response, please try again')

                if not view_info['errors']:
                    # Authenticate user
                    auth_token = auth_email + auth_passwd
                    hash_passwd = hashlib.sha1(auth_token).hexdigest()
                    auth_user_id = db.auth_users.insert(
                        auth_email=auth_email,
                        auth_passwd=hash_passwd,
                        auth_created_on=request.now,
                        auth_modified_on=request.now)
                    # Add the default role of zMember
                    # (NOTE: THIS ROLE MUST EXIST)
                    auth_role_id = db(
                        db.auth_roles.auth_role_name=='zMember').select(
                        db.auth_roles.id)[0].id
                    db.auth_user_role.insert(auth_user_id=auth_user_id,
                                             auth_role_id=auth_role_id)
                    # Now authenticate user
                    auth_user.authenticate(auth_email, auth_passwd)
            else:
                view_info['errors'].append('Please make sure you fill in all '
                                           'the required fields in order to '
                                           'continue')

            if view_info['errors']:
                return dict(request=request, view_info=view_info)
            else:
                redirect(URL(r=request, c='default', f='index'))
        else:
            redirect(URL(r=request, c='default', f='index'))
    else:
        return dict(request=request, view_info=view_info)

def view_topic():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    
    # !MODFIED CODE:
    #     Added 'can_embed' to security_info values
    security_info = {'can_add': False, 'can_reply': False, 'can_edit': False, 'can_embed': False}
    # !END MODIFIED CODE
    
    parent_topic_removed = False
    user_id = auth_user.get_user_id() or 0
    emoticons = ['icon_arrow.png', 'icon_biggrin.png', 'icon_confused.png',
                 'icon_cool.png', 'icon_cry.png', 'icon_exclaim.png',
                 'icon_idea.png', 'icon_lol.png', 'icon_mad.png',
                 'icon_mrgreen.png', 'icon_neutral.png', 'icon_question.png',
                 'icon_razz.png', 'icon_redface.png', 'icon_rolleyes.png',
                 'icon_sad.png', 'icon_smile.png', 'icon_twisted.png',
                 'icon_wink.png']
                 
    # !NEW CODE:
    #     Add list of font effects and and video source icons to
    #     view_info object to allow add_topic view to implement
    #     buttons based on those values.
    view_info.update({'emoticons': emoticons})
    font_effects = ['B', 'I', 'U']
    view_info.update({'font_effects': font_effects})
    video_icons = ['icon_youtube.png',
                   'icon_vimeo.png']
    view_info.update({'video_icons': video_icons})
    # !END NEW CODE
    
    # Added in 1.0.3 - Captcha-like
    captcha = forumhelper.gen_pwd()
    view_info['anon_captcha'] = captcha
    view_info['anon_captcha_base64'] = base64.standard_b64encode(captcha)

    if req.form_submitted:
        topic_id = (req.topic_id)
    else:
        topic_id = int(request.args(0))
    # Get This topic
    topic = db(db.zf_topic.id==topic_id).select()[0]
    if topic.parent_flag:

        # Handle Topic subscriptions here
        if len(request.args) > 1:
            subscription_request = int(request.args[1]) == 1
            if subscription_request:
                forumhelper.add_topic_subscription(topic_id, user_id)
            else:
                forumhelper.del_topic_subscription(topic_id, user_id)

        # Handle Topic Hits Here as well
        db(db.zf_topic.id == topic_id).update(hits=topic.hits+1)

        # Grab the forum
        forum = db(db.zf_forum.id == topic.forum_id).select()[0]

        if len(forum.add_postings_access_roles):
            security_info['can_add'] = [
                role for role in auth_user.get_roles()
                if forum.add_postings_access_roles.find(role)] != []
        else:
            security_info['can_add'] = True

        if len(forum.reply_postings_access_roles):
            security_info['can_reply'] = [
                role for role in auth_user.get_roles()
                if forum.reply_postings_access_roles.find(role)] != []
        else:
            security_info['can_reply'] = True
            
        # !NEW CODE:
        #     This code sets the can_embed flag based on whether the user has the zMemberMedia role
        #     or is an admin. It sets the can_edit flag, used to determine whether user can edit
        #     parent post in a thread, based on whether they're logged in and created that post.
        if auth_user.is_auth() and (auth_user.has_role('zMemberMedia') or auth_user.is_admin()):
            security_info['can_embed'] = True
        else:
            security_info['can_embed'] = False
        
        if auth_user.is_auth() and auth_user.get_user_id() == topic.creation_user_id:
            security_info['can_edit'] = True
        else:
            security_info['can_edit'] = False
        # !END NEW CODE

        # HANDLE Removals/Submission of new topic, etc
        # Was a removal requested?
        if req.remove and auth_user.is_admin():
            # At this point, there are several important things to consider,
            # if the admin requested removal of the parent topic, along with
            # one or more children topics, there is no point in processing
            # the children since they'll be deleted anyway
            if req.get('remove_topic_parent_%s' % (topic_id), '') != '':
                # Removal of parent requested, remove children first,
                # then parent.
                db(db.zf_topic.parent_id==topic_id).delete()
                db(db.zf_topic.id==topic_id).delete()
                parent_topic_removed = True
            else:
                # Removal of certain children topics requested only
                for req_var in req:
                    if req_var[:19] == 'remove_topic_child_':
                        child_topic_id = int(req[req_var])
                        db(db.zf_topic.id == child_topic_id).delete()
        if parent_topic_removed:
            redirect(URL(r=request, c='default', f='view_forum',
                         args=[forum.id]))
        else:

            # Here now check if the user is trying to add a new response
            # (or preview)
            if req.preview:
                view_info.update({'preview': True})
            elif req.form_submitted and security_info['can_reply'] and not \
                auth_user.is_auth() and \
                base64.standard_b64encode(req.captcha_response) != req.c:
                # Use this slot when captcha fails
                # This test must be evaluated when:
                # - The User is Anonymous
                # - AND the forum allow anonymous replies
                view_info['errors'].append('Please make sure all required '
                                           'fields are properly filled')
                view_info.update({'preview': True})
            elif req.add and (security_info['can_reply'] or \
                              auth_user.is_admin()):
                if req.response_content.strip():
                    now = request.now.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # !NEW CODE:
                    #     This removes the media-specific tags from a post before submitting it
                    #     if the user does not have permission to embed media. The resulting post
                    #     will contain the URL of the video but not the tags that are translated
                    #     into html embedding code went displayed in the view.
                    contains_media = req.response_content
                    if not auth_user.is_admin() and not auth_user.has_role('zMemberMedia'):
                        req.response_content = req.response_content.replace("[vimeo]", "");
                        req.response_content = req.response_content.replace("[/vimeo]", "");
                        req.response_content = req.response_content.replace("[youtube]", "");
                        req.response_content = req.response_content.replace("[/youtube]", "");
                    # !END NEW CODE    

                    # User is requesting addition of a response (child topic)
                    db.zf_topic.insert(forum_id=forum.id,
                        title=topic.title,
                        content=req.response_content,
                        parent_id=topic_id,
                        creation_user_id=user_id,
                        creation_date=now,
                        modifying_user_id=user_id,
                        modifying_date=now,
                        hits=0,
                        parent_flag=False,
                        locked_flag=False,
                        disabled_flag=False,
                        sticky_flag=False,
                        poll_flag=False,
                        system_announcement_flag=False,
                        reply_to_topic_id=0,
                        ip_address=request.remote_addr)

                    # Update the modifying date, and the modifying user of
                    # its parent also
                    db(db.zf_topic.id == topic_id).update(
                        modifying_date=now,
                        modifying_user_id=user_id)

                    # Increment the number of postings for this user
                    # IF the user is not anonymous
                    if user_id:
                        postings = int(forumhelper.get_member_property(
                            'zfmp_postings', user_id, '0')) + 1
                        forumhelper.put_member_property('zfmp_postings',
                                                        user_id, str(postings))

                    # Notify Subscribed users about changes in this topic
                    forumhelper.setup_notifications(subscription_id=topic_id,
                                                    subscription_type='T',
                                                    now=request.now)

                else:
                    view_info['errors'].append('Content must be specified for '
                                               'the reply')

            # Information to pass regarding system variables, etc
            # Topic Subscription:
            view_info.update({'subscribed_to_topic':
                forumhelper.has_topic_subscription(topic_id, user_id)})

            # Pagination Manager Part I/II
            start = int(req.get('start', 0))
            responses_per_page = int(forumhelper.get_system_property(
                'zfsp_responses_per_page', 15))
            # Children Topics
            all_children = db(db.zf_topic.parent_id == topic.id).count()
            children = db(db.zf_topic.parent_id == topic.id).select(
                db.zf_topic.ALL, orderby=db.zf_topic.modifying_date,
                limitby=(start, start+responses_per_page))

            # Pagination Manager Part II/II
            pagination_widget = forumhelper.pagination_widget(
                all_children, start, URL(r=request,
                                         c='default',
                                         f='view_topic',
                                         args=[topic_id]), 'topic')
            view_info.update({'pagination_widget': pagination_widget})

            return dict(request=request,
                        security_info=security_info,
                        forum=forum,
                        topic=topic,
                        children=children,
                        view_info=view_info)
    else:
        redirect(URL(r=request, c='default', f='invalid_request'))

def add_topic():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    view_info['messages'] = []
    captcha = forumhelper.gen_pwd()
    view_info['anon_captcha'] = captcha
    view_info['anon_captcha_base64'] = base64.standard_b64encode(captcha)
    
    # !NEW CODE:
    #     The new ability 'can_embed' is added to the security_info
    #     object and its value is set based on whether the user has the
    #     new zMemberMedia role.
    security_info = {'can_add': False, 'can_reply': False, 'can_embed': False}
    if auth_user.is_auth() and auth_user.has_role('zMemberMedia'):
        security_info['can_embed'] = True
    # !END NEW CODE
    
    is_admin = auth_user.has_role('zAdministrator')
    emoticons = ['icon_arrow.png',
                 'icon_biggrin.png',
                 'icon_confused.png',
                 'icon_cool.png',
                 'icon_cry.png',
                 'icon_exclaim.png',
                 'icon_idea.png',
                 'icon_lol.png',
                 'icon_mad.png',
                 'icon_mrgreen.png',
                 'icon_neutral.png',
                 'icon_question.png',
                 'icon_razz.png',
                 'icon_redface.png',
                 'icon_rolleyes.png',
                 'icon_sad.png',
                 'icon_smile.png',
                 'icon_twisted.png',
                 'icon_wink.png']
    view_info.update({'emoticons': emoticons})
   
    # !NEW CODE:
    #     Add list of font effects and and video source icons to
    #     view_info object to allow add_topic view to implement
    #     buttons based on those values.
    font_effects = ['B','I','U']
    view_info.update({'font_effects': font_effects})
    video_icons = ['icon_youtube.png',
                   'icon_vimeo.png']
    view_info.update({'video_icons': video_icons})
    # !END NEW CODE
    
    if req.form_submitted:
        forum_id = int(req.forum_id)
        if req.add_topic:
            # First thing, required fields check:
            if (req.title and req.content) and (auth_user.is_auth() or (
                not auth_user.is_auth() and base64.standard_b64encode(
                    req.captcha_response) == req.c)):
                content = req.content
                # Parse the title
                # Ignore ALL html tags AND do not convert it
                title = parse_content(req.title)

                creation_user = auth_user.get_user_id() or 0
                modifying_user = creation_user
                if is_admin:
                    locked_flag = req.locked_flag is not None
                    sticky_flag = req.sticky_flag is not None
                    system_announcement_flag = req.system_announcement_flag \
                                               is not None
                    creation_date = req.creation_date
                    modifying_date = req.modifying_date
                else:
                    locked_flag = False
                    sticky_flag = False
                    system_announcement_flag = False
                    creation_date = request.now
                    modifying_date = creation_date

                # Add Signature from Member Profile if requested.
                if req.add_signature:
                    signature = forumhelper.get_member_property(
                        'zfmp_signature', creation_user, '')
                    if signature:
                        content += '\n\n<code>\n%s</code>' % (signature)

                # !NEW CODE:
                #     This removes the media-specific tags from a post before submitting it
                #     if the user does not have permission to embed media. The resulting post
                #     will contain the URL of the video but not the tags that are translated
                #     into html embedding code went displayed in the view.
                contains_media = req.content
                if not auth_user.is_admin() and not auth_user.has_role('zMemberMedia'):
                    req.content= req.content.replace("[vimeo]", "");
                    req.content= req.content.replace("[/vimeo]", "");
                    req.content= req.content.replace("[youtube]", "");
                    req.content= req.content.replace("[/youtube]", "");
                # !END NEW CODE   

                # Add the topic
                topic_id = db.zf_topic.insert(forum_id=forum_id,
                    title=title,
                    content=content,
                    creation_user_id=creation_user,
                    creation_date=creation_date,
                    modifying_user_id=modifying_user,
                    modifying_date=modifying_date,
                    parent_flag=True,
                    locked_flag=locked_flag,
                    disabled_flag=False,
                    sticky_flag=sticky_flag,
                    poll_flag=False,
                    system_announcement_flag=system_announcement_flag,
                    ip_address=request.remote_addr)

                # Notify Subscribed users about changes in this Forum
                forumhelper.setup_notifications(subscription_id=forum_id,
                                                subscription_type='F',
                                                now=request.now)

                # Subscribe user to topic if requested
                if req.add_subscription:
                    forumhelper.add_topic_subscription(topic_id,
                                                       creation_user) # ID

                # Increment the number of postings for this user
                postings = int(forumhelper.get_member_property(
                    'zfmp_postings', creation_user, '0')) + 1
                forumhelper.put_member_property('zfmp_postings',
                                                creation_user,
                                                str(postings))

                view_info['messages'].append('Topic has been added')
                redirect(URL(r=request,
                             c='default',
                             f='view_forum',
                             args=[forum_id],
                             vars=dict(added='1')))
            else:
                view_info['errors'].append('Please make sure all required '
                                           'fields are properly filled')
                return dict(request=request,
                            view_info=view_info,
                            forum_id=forum_id, security_info=security_info)
        elif req.preview_b:
            content = req.content
            if is_admin:
                creation_user = req.creation_user
            else:
                creation_user = auth_user.get_user_id()
            # Add Signature from Member Profile if requested.
            if req.add_signature:
                signature = forumhelper.get_member_property('zfmp_signature',
                                                            creation_user,
                                                            '')
                if signature:
                    content += '\n\n<code>\n%s</code>' % (signature)
            view_info.update({'preview': content})
           
            # !MODIFIED CODE:
            #     Added security_security_info to the dictionary.
            return dict(request=request,
                        view_info=view_info,
                        forum_id=forum_id,
                        security_info=security_info)
            # !END MODIFIED CODE
            
        else:
            redirect(URL(r=request,
                         c='default',
                         f='view_forum',
                         args=[forum_id]))
    else:
        forum_id = int(request.args[0])
        return dict(request=request, view_info=view_info, forum_id=forum_id, security_info=security_info)

# !NEW FUNCTION: add_profile_topic
#         Based on the add_topic function, this handles the special case of adding
#     a topic to a user's profile. All profile threads are stored in the same
#     location and we know who the user is because they are logged in, so it takes
#     no input. Upon successfully adding a topic, the user is redirected to their own 
#     edit_profile page.
@auth_user.requires_login()
def add_profile_topic():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    view_info['messages'] = []
    captcha = forumhelper.gen_pwd()
    view_info['anon_captcha'] = captcha
    view_info['anon_captcha_base64'] = base64.standard_b64encode(captcha)
    
    forum_id = db(db.zf_forum.forum_title=="Profile").select(db.zf_forum.id).first()
    security_info = {'can_add': False, 'can_reply': False, 'can_embed': False}
    if auth_user.has_role('zMemberMedia') or auth_user.is_admin():
        security_info['can_embed'] = True
    is_admin = auth_user.has_role('zAdministrator')
    emoticons = ['icon_arrow.png',
                 'icon_biggrin.png',
                 'icon_confused.png',
                 'icon_cool.png',
                 'icon_cry.png',
                 'icon_exclaim.png',
                 'icon_idea.png',
                 'icon_lol.png',
                 'icon_mad.png',
                 'icon_mrgreen.png',
                 'icon_neutral.png',
                 'icon_question.png',
                 'icon_razz.png',
                 'icon_redface.png',
                 'icon_rolleyes.png',
                 'icon_sad.png',
                 'icon_smile.png',
                 'icon_twisted.png',
                 'icon_wink.png']
    view_info.update({'emoticons': emoticons})
    view_info.update({'emoticons': emoticons})
    font_effects = ['B','I','U']
    view_info.update({'font_effects': font_effects})
    video_icons = ['icon_youtube.png',
                   'icon_vimeo.png']
    view_info.update({'video_icons': video_icons})
    if req.form_submitted:
        if req.add_topic:
            # First thing, required fields check:
            if (req.title and req.content) and (auth_user.is_auth() or (
                not auth_user.is_auth() and base64.standard_b64encode(
                    req.captcha_response) == req.c)):
                content = req.content
                # Parse the title
                # Ignore ALL html tags AND do not convert it
                title = parse_content(req.title)

                creation_user = auth_user.get_user_id() or 0
                modifying_user = creation_user
                if is_admin:
                    locked_flag = req.locked_flag is not None
                    sticky_flag = req.sticky_flag is not None
                    system_announcement_flag = req.system_announcement_flag \
                                               is not None
                    creation_date = req.creation_date
                    modifying_date = req.modifying_date
                else:
                    locked_flag = False
                    sticky_flag = False
                    system_announcement_flag = False
                    creation_date = request.now
                    modifying_date = creation_date

                # Add Signature from Member Profile if requested.
                if req.add_signature:
                    signature = forumhelper.get_member_property(
                        'zfmp_signature', creation_user, '')
                    if signature:
                        content += '\n\n<code>\n%s</code>' % (signature)

                contains_media = req.content
                if not auth_user.is_admin() and not auth_user.has_role('zMemberMedia'):
                    req.content= req.content.replace("[vimeo]", "");
                    req.content= req.content.replace("[/vimeo]", "");
                    req.content= req.content.replace("[youtube]", "");
                    req.content= req.content.replace("[/youtube]", "");  
                
                # Add the topic
                topic_id = db.zf_topic.insert(forum_id=forum_id,
                    title=title,
                    content=content,
                    creation_user_id=creation_user,
                    creation_date=creation_date,
                    modifying_user_id=modifying_user,
                    modifying_date=modifying_date,
                    parent_flag=True,
                    locked_flag=locked_flag,
                    disabled_flag=False,
                    sticky_flag=sticky_flag,
                    poll_flag=False,
                    system_announcement_flag=system_announcement_flag,
                    ip_address=request.remote_addr)

                # Notify Subscribed users about changes in this Forum
                forumhelper.setup_notifications(subscription_id=forum_id,
                                                subscription_type='F',
                                                now=request.now)

                # Subscribe user to topic if requested
                if req.add_subscription:
                    forumhelper.add_topic_subscription(topic_id,
                                                       creation_user) # ID

                # Increment the number of postings for this user
                postings = int(forumhelper.get_member_property(
                    'zfmp_postings', creation_user, '0')) + 1
                forumhelper.put_member_property('zfmp_postings',
                                                creation_user,
                                                str(postings))

                view_info['messages'].append('Topic has been added')
                redirect(URL(r=request,
                             c='default',
                             f='edit_profile',
                             vars=dict(added='1')))
            else:
                view_info['errors'].append('Please make sure all required '
                                           'fields are properly filled')
                return dict(request=request,
                            view_info=view_info,
                            forum_id=forum_id,
                            security_info=security_info)
        elif req.preview_b:
            content = req.content
            if is_admin:
                creation_user = req.creation_user
            else:
                creation_user = auth_user.get_user_id()
            # Add Signature from Member Profile if requested.
            if req.add_signature:
                signature = forumhelper.get_member_property('zfmp_signature',
                                                            creation_user,
                                                            '')
                if signature:
                    content += '\n\n<code>\n%s</code>' % (signature)
            view_info.update({'preview': content})
            return dict(request=request,
                        view_info=view_info,
                        forum_id=forum_id,
                        security_info=security_info)
        else:
            redirect(URL(r=request,
                         c='default',
                         f='edit_profile'))

    else:
        return dict(request=request, view_info=view_info, forum_id=forum_id, security_info=security_info)
# !END NEW FUNCTION

# !NEW FUNCTION: edit_profile
#         This function is partially based on the old preferences function.
#     It loads the information of the logged in user - their name, email, 
#     location, etc and whether those values are currently set as 
#     publicly hidden or not. It also loads all referenced/bookmarked threads
#     and all the user's profile-specific threads and whether they are set
#     as publicly hidden.
#         Users can update their information, change the settings to make it hidden or visible,
#     make their selected topics/threads hidden or visible in their public profile, remove
#     the links to referenced threads, and delete profile-specific threads from the system.
@auth_user.requires_login()
def edit_profile():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    view_info['messages'] = []
    view_info['props'] = {}
    ref_topic_id = ""
    user_id = auth_user.get_user_id()
    
    # User is trying to add a new topic to the list of referened topics
    if request.args(0)=='add_ref':
        ref_topic_id = int(request.args(1))
        # Pull information on topic, forum and containing category
        topic = db(db.zf_topic.id==ref_topic_id).select()[0]#.first()
        forum = db(db.zf_forum.id==topic.forum_id).select()[0]#.first()
        cat = db(db.zf_forum_category.id==forum.cat_id).select()[0]#.first()
        # Check whether this thread already exists for user profile
        exists = db((db.zf_referenced_topic.topic_id==topic.id) & (db.zf_referenced_topic.user_id==auth_user.get_user_id())).select()
        # Only add entry if topic is accessible, not disabled/locked, a parent topic, and not already linked in the db
        if (cat.cat_visible_to.find('zAdministrator') == -1 or (cat.cat_name=="Administration" and forum.forum_title=="Profile")) and (not topic.disabled_flag and not topic.locked_flag and topic.parent_flag) and not exists:
            db.zf_referenced_topic.insert(user_id=auth_user.get_user_id(), topic_id=topic.id)
    
    # User is trying to add a friend to friendslist and new friend not already on friendslist
    elif request.args(0) == 'add_friend' and not forumhelper.get_friend_status(user_id, int(request.args(1))):
        db.zf_friend_user.insert(self_id=user_id, target_id=int(request.args(1)))
    # User is trying to remove a friend from friendslist
    elif request.args(0) == 'remove_friend' and forumhelper.get_friend_status(user_id, int(request.args(1))):
        db((db.zf_friend_user.self_id==user_id) & (db.zf_friend_user.target_id==int(request.args(1)))).delete()

    
    AVATAR_MAX_HEIGHT = 100
    AVATAR_MAX_WIDTH  = 120
    AVATAR_MAX_SIZE   = 15000 # Bytes
    user_email = db(db.auth_users.id == user_id).select(
        db.auth_users.auth_email).first().auth_email

    # User has submitted an update to profile information
    if req.form_details_submitted:
        if req.update_b:
            # Standard Properties
            forumhelper.put_member_property('zfmp_real_name', user_id, 
                                            req.real_name)
            forumhelper.put_member_property_hidden('zfmp_real_name', user_id, 
                                            req.cb_real_name)                                                      
            forumhelper.put_member_property('zfmp_web_page', user_id,
                                            req.web_page)
            forumhelper.put_member_property_hidden('zfmp_web_page', user_id,
                                            req.cb_web_page)                                            
            forumhelper.put_member_property('zfmp_country', user_id,
                                            req.country)
            forumhelper.put_member_property_hidden('zfmp_country', user_id,
                                            req.cb_country)                                            
            forumhelper.put_member_property('zfmp_signature', user_id,
                                            req.signature)
            forumhelper.put_member_property_hidden('zfmp_signature', user_id,
                                            req.cb_signature)                                            
            forumhelper.put_member_property('zfmp_locale', user_id,
                                            req.locale)                                           
            forumhelper.put_member_property('zfmp_user_info', user_id, 
                                            req.user_info)
            forumhelper.put_member_property_hidden('zfmp_user_info', user_id, 
                                            req.cb_user_info)
            if req.allow_pm_use:
                zfmp_allow_pm_use = "1"
            else:
                zfmp_allow_pm_use = ""
            forumhelper.put_member_property('zfmp_allow_pm_use', user_id,
                                            zfmp_allow_pm_use)

            # Check for valid update of username - don't allow duplicates
            username = req.username.strip()
            if username:
                if db(
                    (db.zf_member_properties.property_value.lower() == \
                     username.lower()) &
                    (db.zf_member_properties.property_id == \
                     db.zf_member_properties_skel.id) &
                    (db.zf_member_properties_skel.property_name == \
                     'zfmp_display_name') &
                    (db.zf_member_properties.user_id != user_id)).count():
                        view_info['errors'].append('This username already '
                                                   'exists, please choose '
                                                   'another one')
                else:
                    forumhelper.put_member_property('zfmp_display_name',
                                                    user_id, username)
            else:
                view_info['errors'].append('The Username value cannot be '
                                           'empty')

            # Topic Subscriptions
            remove_topic_subscription = req.remove_topic_subscription
            if remove_topic_subscription:
                if type(remove_topic_subscription) == type([]):
                    for topic_id in remove_topic_subscription:
                        forumhelper.del_topic_subscription(int(topic_id),
                                                           user_id)
                else:
                    forumhelper.del_topic_subscription(
                        int(remove_topic_subscription), user_id)

            # Forum Subscriptions
            remove_forum_subscription = req.remove_forum_subscription
            if remove_forum_subscription:
                if type(remove_forum_subscription) == type([]):
                    for forum_id in remove_forum_subscription:
                        forumhelper.del_forum_subscription(int(forum_id),
                                                           user_id)
                else:
                    forumhelper.del_forum_subscription(
                        int(remove_forum_subscription), user_id)

            # Password Changes
            if req.new_passwd or req.new_passwd_confirm:
                if req.new_passwd == req.new_passwd_confirm:
                    hash_passwd = hashlib.sha1(
                        auth_user.get_user_name() + req.new_passwd).hexdigest()
                    db(db.auth_users.id == user_id).update(
                        auth_passwd=hash_passwd)
                else:
                    view_info['errors'].append('Password and confirmation do '
                                               'not match, please try again')

            # Avatars
            if req.remove_avatar:
                db(db.zf_member_avatars.user_id == user_id).update(
                    avatar_active=False)

            # Selected Language (allow storing the "default"
            # value (an empty string))
            forumhelper.put_member_property('zfmp_locale', user_id,
                                            req.lang_code)

            # Crude verification of a FileUpload object set
            try:
                filename = req.avatar_data.filename
            except AttributeError:
                filename = ''

            if filename:
                # Resource: http://epydoc.sourceforge.net/stdlib/cgi.
                # FieldStorage-class.html
                image_data = req.avatar_data.file.read()
                content_type = req.avatar_data.type # "image/png"
                doc_type, ext = content_type.split('/')
                if doc_type == 'image':
                    c_type, width, height = forumhelper.get_image_info(
                        image_data)
                    update_avatar = True
                    if height > AVATAR_MAX_HEIGHT or width > AVATAR_MAX_WIDTH:
                        view_info['errors'].append('Image dimensions exceed '
                                                   'the limits set by the '
                                                   'administrator: (H:'
                                                   '%spx, W:%spx)' % (height,
                                                                      width))
                        update_avatar = False
                    if len(image_data) > AVATAR_MAX_SIZE:
                        view_info['errors'].append('Avatar exceeds the '
                                                   'maximum image size set by '
                                                   'the administrator: '
                                                   '%s bytes' % (
                                                    len(image_data)))
                        update_avatar = False

                    if update_avatar:
                        if forumhelper.has_member_avatar(user_id,
                                                         bypass=False):
                            # Update:
                            db(db.zf_member_avatars.user_id==user_id).update(
                                content_type=content_type,
                                avatar_image=image_data, avatar_active=True)
                        else:
                            # Add:
                            db.zf_member_avatars.insert(
                                content_type=content_type,
                                user_id=user_id,
                                avatar_image=image_data, avatar_active=True)

            if view_info['errors']:
                return dict(request=request, view_info=view_info,
                            user_id=user_id, user_email=user_email,
                            forum_subscriptions=forum_subscriptions,
                            topic_subscriptions=topic_subscriptions,
                            available_languages=available_languages,
                            friendslist=friendslist)
            else:
                redirect(URL(r=request, c='default', f='edit_profile',
                             vars=dict(lang=req.lang_code, upd=1)))

    # Get current values for user properties and whether those values are hidden    
    view_info['props'].update({'real_name':
        forumhelper.get_member_property('zfmp_real_name', user_id, '')})
    view_info['props'].update({'real_name_hidden':
        forumhelper.get_member_property_hidden('zfmp_real_name', user_id, False)})            
    view_info['props'].update({'web_page':
        forumhelper.get_member_property('zfmp_web_page', user_id, '')})
    view_info['props'].update({'web_page_hidden':
        forumhelper.get_member_property_hidden('zfmp_web_page', user_id, False)})        
    view_info['props'].update({'country':
        forumhelper.get_member_property('zfmp_country', user_id, '')})
    view_info['props'].update({'country_hidden':
        forumhelper.get_member_property_hidden('zfmp_country', user_id, False)})        
    view_info['props'].update({'signature':
        forumhelper.get_member_property('zfmp_signature', user_id, '')})
    view_info['props'].update({'signature_hidden':
        forumhelper.get_member_property_hidden('zfmp_signature', user_id, False)})       
    view_info['props'].update({'locale':
        forumhelper.get_member_property('zfmp_locale', user_id, '')})
    view_info['props'].update({'locale_hidden':
        forumhelper.get_member_property_hidden('zfmp_locale', user_id, False)})        
    view_info['props'].update({'allow_pm_use':
        forumhelper.get_member_property('zfmp_allow_pm_use', user_id, '')})        
    view_info['props'].update({'postings':
        forumhelper.get_member_property('zfmp_postings', user_id, '0')})
    view_info['props'].update({'postings_hidden':
        forumhelper.get_member_property('zfmp_postings_hidden', user_id, False)})        
    view_info['props'].update({'last_login':
        forumhelper.get_member_property(
            'zfmp_last_login', user_id, str(XML(T('Never'))))})
    view_info['props'].update({'last_login_hidden':
        forumhelper.get_member_property_hidden(
            'zfmp_last_login', user_id, False)})                    
    view_info['props'].update({'username':
        forumhelper.get_member_property(
            'zfmp_display_name', user_id, 'user_%s' % (user_id))})            
    view_info['props'].update({'user_info':
        forumhelper.get_member_property('zfmp_user_info', user_id, '')})
    view_info['props'].update({'user_info_hidden':
        forumhelper.get_member_property_hidden('zfmp_user_info', user_id, '')})
        
    forum_subscriptions = db((db.zf_member_subscriptions.user_id == user_id) &
        (db.zf_member_subscriptions.subscription_type == 'F') &
        (db.zf_member_subscriptions.subscription_id == db.zf_forum.id) &
        (db.zf_member_subscriptions.subscription_active == True)).select(
        db.zf_forum.id, db.zf_forum.forum_title)
    topic_subscriptions = db((db.zf_member_subscriptions.user_id == user_id) &
        (db.zf_member_subscriptions.subscription_type == 'T') &
        (db.zf_member_subscriptions.subscription_id == db.zf_topic.id) &
        (db.zf_member_subscriptions.subscription_active == True)).select(
        db.zf_topic.id, db.zf_topic.title)
    available_languages = db(db.zf_available_languages.enabled == True).select(
        db.zf_available_languages.ALL,
        orderby=db.zf_available_languages.language_desc)
        
    # Handle referenced/profile threads
    # Pagination Manager Part I/II
    start_1 = int(req.get('start_1', 0))
    start_2 = int(req.get('start_2', 0))
    #try:
    topics_per_page = int(
        forumhelper.get_system_property('zfsp_threads_per_page', 15))
    
    # Select the profile threads and the referenced threads for this user
    user_id = auth_user.get_user_id()
    temp_cat = db(db.zf_forum_category.cat_name=="Administration").select(db.zf_forum_category.id).first()
    forum_id = db((db.zf_forum.forum_title=="Profile") & (db.zf_forum.cat_id==temp_cat)).select(db.zf_forum.id).first()
    my_threads = db((db.zf_topic.parent_flag==True) & (db.zf_topic.forum_id==forum_id) & (db.zf_topic.creation_user_id==user_id)).select(db.zf_topic.ALL,limitby=(start_1, start_1+topics_per_page))
    my_ref_threads = db((db.zf_referenced_topic.user_id==user_id) & (db.zf_referenced_topic.topic_id==db.zf_topic.id)).select(limitby = (start_2, start_2 + topics_per_page))
    
    # Profile threads are being updated 
    if req.up_topics_1:
        # Loop through and unhide all profile topics - essentially, reset the values before seeing what the user wants to change them to
        for topic in my_threads:
            db(db.zf_topic.id==topic.id).validate_and_update(profile_hidden=False)
        # Check for user input
        for req_var in req:
            # User wants profile topic hidden
            if req_var[:13] == 'hide_topic_1_':
                hide_topic_id = int(req[req_var])
                db(db.zf_topic.id==hide_topic_id).validate_and_update(profile_hidden=True)
                view_info.update({'topics_hidden': True})
            # User wants a profile topic deleted
            elif req_var[:12] == 'del_topic_1_':
                del_topic_id = int(req[req_var])
                db(db.zf_topic.parent_id==del_topic_id).delete() # Children
                db(db.zf_topic.id==del_topic_id).delete() # Parent
                view_info.update({'topics_removed': True})
    
    # Referenced threads are being updated              
    if req.up_topics_2:
        # Again, reset the hidden values to false before processing user input
        for topic in my_ref_threads:
            db((db.zf_referenced_topic.topic_id==topic.zf_topic.id) & (db.zf_referenced_topic.user_id==user_id)).validate_and_update(profile_hidden=False)
        for req_var in req:
            # User wants to hide a referenced topic
            if req_var[:13] == 'hide_topic_2_':
                hide_topic_id = int(req_var[13:])#int(req[req_var])
                db(db.zf_referenced_topic.topic_id==hide_topic_id).update(profile_hidden=True)
                #db(db.zf_topic.topic_name=='bogus').select()[0]
                view_info.update({'topics_hidden': True})
            # User wants to delete the profile reference to a topic
            if req_var[:12] == 'del_topic_2_':
                del_topic_id = int(req[req_var])
                db((db.zf_referenced_topic.topic_id==del_topic_id) & (db.zf_referenced_topic.user_id==user_id)).delete()
                view_info.update({'topics_removed': True})    
                
    # Friendslist is being updated
    if req.up_friend:
        for req_var in req:
            if req_var[:11] == 'del_friend_':
                friend_id = int(req[req_var])
                db((db.zf_friend_user.self_id==user_id) & (db.zf_friend_user.target_id==friend_id)).delete()                     
    # Grab friendslist
    friendslist = db(db.zf_friend_user.self_id==user_id).select()
    
    view_info.update({'zfsp_topic_teaser_length':
        int(forumhelper.get_system_property('zfsp_topic_teaser_length', 250))})
    
    # Refresh information on user and threads
    my_self = db(db.auth_users.id==user_id).select().first()
    my_threads = db((db.zf_topic.parent_flag==True) & (db.zf_topic.forum_id==forum_id) & (db.zf_topic.creation_user_id==user_id)).select(db.zf_topic.ALL,limitby=(start_1, start_1+topics_per_page))
    my_ref_threads = db((db.zf_referenced_topic.user_id==user_id) & (db.zf_referenced_topic.topic_id==db.zf_topic.id)).select(limitby = (start_2, start_2 + topics_per_page))
    
    # Pagination Manager Part II/II
    pagination_widget_1 = forumhelper.pagination_widget(
        len(my_threads),
        start_1,
        URL(r=request, c='default', f='edit_profile', args=[]),'forum')
    view_info.update({'pagination_widget_1': pagination_widget_1})
    pagination_widget_2 = forumhelper.pagination_widget(
        len(my_ref_threads),
        start_2,
        URL(r=request, c='default', f='edit_profile', args=[]),'forum')
    view_info.update({'pagination_widget_2': pagination_widget_2})
    
    topic_1_replies_info = {}
    for topic in my_threads:
        # Get the number of children topics for this (parent) topic
        topic_1_replies_info.update({topic.id:
            db(db.zf_topic.parent_id==topic.id).count()})
    topic_2_replies_info = {}
    for topic in my_ref_threads:
        # Get the number of children topics for this (parent) topic
        topic_2_replies_info.update({topic.zf_topic.id:
            db(db.zf_topic.parent_id==topic.zf_topic.id).count()})
                
    return dict(request=request, view_info=view_info, my_threads=my_threads, my_ref_threads=my_ref_threads, 
                topic_1_replies_info=topic_1_replies_info, topic_2_replies_info=topic_2_replies_info,
                user_id=user_id, user_email=user_email, forum_subscriptions=forum_subscriptions,
                available_languages=available_languages, topic_subscriptions=topic_subscriptions, 
                friendslist=friendslist)
# !END NEW FUNCTION

# !NEW FUNCTION: view_profile
#         This function takes a user's id as a request arg and displays all information 
#     the user has not set to hidden. This includes their profile threads and referenced
#     threads. On the view side, it also allows users to pm the profile's owner and to 
#     reference that user's profile threads in their own profiles.  
def view_profile():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    view_info['messages'] = []
    view_info['props'] = {}
    ref_topic_id = ""
    user_id = request.args(0)
    
    # Gather user information to display/edit
    AVATAR_MAX_HEIGHT = 100
    AVATAR_MAX_WIDTH  = 120
    AVATAR_MAX_SIZE   = 15000 # Bytes
    user_email = db(db.auth_users.id == user_id).select(
        db.auth_users.auth_email).first().auth_email
    
    view_info['props'].update({'real_name':
        forumhelper.get_member_property('zfmp_real_name', user_id, '')})
    view_info['props'].update({'real_name_hidden':
        forumhelper.get_member_property_hidden('zfmp_real_name', user_id, False)})            
    view_info['props'].update({'web_page':
        forumhelper.get_member_property('zfmp_web_page', user_id, '')})
    view_info['props'].update({'web_page_hidden':
        forumhelper.get_member_property_hidden('zfmp_web_page', user_id, False)})        
    view_info['props'].update({'country':
        forumhelper.get_member_property('zfmp_country', user_id, '')})
    view_info['props'].update({'country_hidden':
        forumhelper.get_member_property_hidden('zfmp_country', user_id, False)})        
    view_info['props'].update({'signature':
        forumhelper.get_member_property('zfmp_signature', user_id, '')})
    view_info['props'].update({'signature_hidden':
        forumhelper.get_member_property_hidden('zfmp_signature', user_id, False)})       
    view_info['props'].update({'locale':
        forumhelper.get_member_property('zfmp_locale', user_id, '')})
    view_info['props'].update({'locale_hidden':
        forumhelper.get_member_property_hidden('zfmp_locale', user_id, False)})        
    view_info['props'].update({'allow_pm_use':
        forumhelper.get_member_property('zfmp_allow_pm_use', user_id, '')})        
    view_info['props'].update({'postings':
        forumhelper.get_member_property('zfmp_postings', user_id, '0')})
    view_info['props'].update({'postings_hidden':
        forumhelper.get_member_property('zfmp_postings_hidden', user_id, False)})        
    view_info['props'].update({'last_login':
        forumhelper.get_member_property(
            'zfmp_last_login', user_id, str(XML(T('Never'))))})
    view_info['props'].update({'last_login_hidden':
        forumhelper.get_member_property_hidden(
            'zfmp_last_login', user_id, False)})                    
    view_info['props'].update({'username':
        forumhelper.get_member_property(
            'zfmp_display_name', user_id, 'user_%s' % (user_id))})            
    view_info['props'].update({'user_info':
        forumhelper.get_member_property('zfmp_user_info', user_id, '')})
    view_info['props'].update({'user_info_hidden':
        forumhelper.get_member_property_hidden('zfmp_user_info', user_id, '')})

    # Handle referenced/profile threads
    # Pagination Manager Part I/II
    start_1 = int(req.get('start_1', 0))
    start_2 = int(req.get('start_2', 0))
    #try:
    topics_per_page = int(
        forumhelper.get_system_property('zfsp_threads_per_page', 15))
    
    # Pull information on user
    temp_cat = db(db.zf_forum_category.cat_name=="Administration").select(db.zf_forum_category.id).first()
    forum_id = db((db.zf_forum.forum_title=="Profile") & (db.zf_forum.cat_id==temp_cat)).select(db.zf_forum.id).first()
    my_threads = db((db.zf_topic.parent_flag==True) & (db.zf_topic.forum_id==forum_id) & (db.zf_topic.creation_user_id==user_id)).select(db.zf_topic.ALL,limitby=(start_1, start_1+topics_per_page))
    my_ref_threads = db((db.zf_referenced_topic.user_id==user_id) & (db.zf_referenced_topic.topic_id==db.zf_topic.id)).select(limitby = (start_2, start_2 + topics_per_page))

    view_info.update({'zfsp_topic_teaser_length':
        int(forumhelper.get_system_property('zfsp_topic_teaser_length', 250))})
    
    # Pagination Manager Part II/II
    pagination_widget_1 = forumhelper.pagination_widget(
        len(my_threads),
        start_1,
        URL(r=request, c='default', f='edit_profile', args=[]),'forum')
    view_info.update({'pagination_widget_1': pagination_widget_1})
    pagination_widget_2 = forumhelper.pagination_widget(
        len(my_ref_threads),
        start_2,
        URL(r=request, c='default', f='edit_profile', args=[]),'forum')
    view_info.update({'pagination_widget_2': pagination_widget_2})
    
    topic_1_replies_info = {}
    for topic in my_threads:
        # Get the number of children topics for this (parent) topic
        topic_1_replies_info.update({topic.id:
            db(db.zf_topic.parent_id==topic.id).count()})
    topic_2_replies_info = {}
    for topic in my_ref_threads:
        # Get the number of children topics for this (parent) topic
        topic_2_replies_info.update({topic.zf_topic.id:
            db(db.zf_topic.parent_id==topic.zf_topic.id).count()})
                
    return dict(request=request, view_info=view_info, my_threads=my_threads, my_ref_threads=my_ref_threads, 
                topic_1_replies_info=topic_1_replies_info, topic_2_replies_info=topic_2_replies_info,
                user_id=user_id)    
# !END NEW FUNCTION
        
        
@auth_user.requires_login()
def edit_topic():
    topic_id = request.args[0]
    topic = db(db.zf_topic.id==topic_id).select().first()
    if not auth_user.is_admin() and (auth_user.get_user_id() != topic.creation_user_id):
        redirect_to = URL(r=request, c='default', f='view_topic',
                                  args=[topic.parent_id])
        redirect(redirect_to)

    req = request.vars
    view_info = {}
    view_info['errors'] = []
    view_info['messages'] = []
    
    # !MODIFIEDCODE:
    #     The new ability 'can_embed' is added to the security_info
    #     object and its value is set based on whether the user has the
    #     new zMemberMedia role.
    security_info = {'can_add': False, 'can_reply': False, 'can_embed': False}
    if auth_user.is_auth() and (auth_user.has_role('zMemberMedia') or auth_user.is_admin()):
        security_info['can_embed'] = True
    # !END MODIFIED CODE
    
    emoticons = ['icon_arrow.png',
                 'icon_biggrin.png',
                 'icon_confused.png',
                 'icon_cool.png',
                 'icon_cry.png',
                 'icon_exclaim.png',
                 'icon_idea.png',
                 'icon_lol.png',
                 'icon_mad.png',
                 'icon_mrgreen.png',
                 'icon_neutral.png',
                 'icon_question.png',
                 'icon_razz.png',
                 'icon_redface.png',
                 'icon_rolleyes.png',
                 'icon_sad.png',
                 'icon_smile.png',
                 'icon_twisted.png',
                 'icon_wink.png']
    view_info.update({'emoticons': emoticons})
    
    # !NEW CODE:
    #     Add list of font effects and and video source icons to
    #     view_info object to allow add_topic view to implement
    #     buttons based on those values.
    view_info.update({'emoticons': emoticons})
    font_effects = ['B', 
                    'I', 
                    'U']
    view_info.update({'font_effects': font_effects})
    video_icons = ['icon_youtube.png',
                   'icon_vimeo.png']
    view_info.update({'video_icons': video_icons})
    # !END NEW CODE
    
    if req.form_submitted:
        topic = db(db.zf_topic.id==topic_id).select()[0]
        forum_id = topic.forum_id

        if req.edit_topic:
            if (req.title and req.content):
                title = parse_content(req.title)
                if auth_user.is_admin():            
                    #creation_user = req.creation_user
                    creation_date = req.creation_date
                    #modifying_user = req.modifying_user
                    modifying_date = req.modifying_date
                else:
                    creation_date = topic.creation_date
                    modifying_date = datetime.datetime.now()
                # !NEW CODE:
                #     This removes the media-specific tags from a post before submitting it
                #     if the user does not have permission to embed media. The resulting post
                #     will contain the URL of the video but not the tags that are translated
                #     into html embedding code went displayed in the view.
                contains_media = req.content
                if not auth_user.is_admin() and not auth_user.has_role('zMemberMedia'):
                    req.content = req.content.replace("[vimeo]", "");
                    req.content = req.content.replace("[/vimeo]", "");
                    req.content = req.content.replace("[youtube]", "");
                    req.content = req.content.replace("[/youtube]", "");
                # !END NEW CODE 

                if topic.parent_flag:
                    parent_topic_id = topic_id
                    locked_flag = req.locked_flag is not None
                    sticky_flag = req.sticky_flag is not None
                    system_announcement_flag = req.system_announcement_flag \
                                               is not None
                    db(db.zf_topic.id==topic_id).update(title=title,
                        content=req.content,
                        #creation_user_id=creation_user,
                        creation_date=creation_date,
                        #modifying_user_id=modifying_user,
                        modifying_date=modifying_date,
                        locked_flag=locked_flag,
                        sticky_flag=sticky_flag,
                        system_announcement_flag=system_announcement_flag)
                else:
                    parent_topic_id = topic.parent_id
                    # Just Update child-required fields
                    db(db.zf_topic.id==topic_id).update(title=title,
                        content=req.content,
                        #creation_user_id=creation_user,
                        creation_date=creation_date,
                        #modifying_user_id=modifying_user,
                        modifying_date=modifying_date)
                redirect(URL(r=request, c='default', f='view_topic',
                             args=[parent_topic_id]))
            else:
                view_info['errors'].append('All fields are required')
                return dict(request=request, topic=topic, view_info=view_info, security_info=security_info)
        elif req.preview_b:
            view_info.update({'preview': True})
            return dict(request=request, view_info=view_info, topic=topic, security_info=security_info)
        elif req.remove_b:
            if topic.parent_flag:
                parent_topic_id = topic_id
                db(db.zf_topic.parent_id==parent_topic_id).delete()
                db(db.zf_topic.id==parent_topic_id).delete()
                redirect_to = URL(r=request, c='default', f='view_forum',
                                  args=[forum_id])
            else:
                parent_topic_id = topic.parent_id
                db(db.zf_topic.id==topic_id).delete()
                redirect_to = URL(r=request, c='default', f='view_topic',
                                  args=[parent_topic_id])
            redirect(redirect_to)
        else:
            if topic.parent_flag:
                parent_topic_id = topic.id
            else:
                parent_topic_id = topic.parent_id
            redirect(URL(r=request, c='default', f='view_topic',
                         args=[parent_topic_id]))
    else:
        topic_id = int(request.args[0])
        topic = db(db.zf_topic.id==topic_id).select()[0]
        return dict(request=request, topic=topic, view_info=view_info, security_info=security_info)

def report_inappropriate():
    topic_id = int(request.args[1])
    child_id = int(request.args[0])
    if auth_user.is_auth():
        db.zf_topic_inappropriate.insert(
            topic_id=topic_id,
            child_id=child_id,
            creation_user_id=auth_user.get_user_id(),
            creation_date=request.now,
            read_flag=False)
    redirect(URL(r=request, c='default', f='view_topic', args=[topic_id]))

def rss():
    import gluon.contrib.rss2 as rss2
    import gluon.contrib.markdown as md

    default_type = 'system'
    if len(request.args) == 1:
        rss_type = request.args[0].lower()
        if not rss_type in ['system', 'latest']:
            rss_type = default_type
    else:
        rss_type = default_type

    if rss_type == 'system':
        title = str(XML(T('pyForum Latest System Topics')))
        descr = str(XML(T('pyForum Latest System Topics')))
        rss_topics = forumhelper.get_system_announcements(include_content=True,
                                                          rss=True)
    else:
        title = str(XML(T('pyForum Latest Topics')))
        descr = str(XML(T('pyForum Latest Topics')))
        rss_topics = forumhelper.get_latest_topics(include_content=True,
                                                   rss=True)

    if rss_topics:
        rss_feed = rss2.RSS2(title = title,
                        link = URL(r=request, c='default', f='index'),
                        description = descr,
                        lastBuildDate = request.now,
                        items = [
                            rss2.RSSItem(
                                title = topic.title,
                                link = URL(r=request, c='default', f='view_topic',
                                           args=[topic.id]),
                                description = parse_content(topic.content,
                                                            'forumfull'),
                                pubDate = topic.modifying_date) \
                            for topic in rss_topics]
                        )
        response.headers['Content-Type'] = 'application/rss+xml'
        return rss2.dumps(rss_feed)
    else:
        redirect(URL(r=request, c='default', f='index', vars=dict(rss_msg='No '
                                                                  'RSS Feed '
                                                                  'Found')))

def contact_admin():
    """ Contact Admin - This can allow anonymous users to post spam, so
    for them, I'll add some 'poor man's captcha'

    """
    view_info = {}
    view_info['errors'] = []
    captcha = forumhelper.gen_pwd()
    view_info['anon_captcha'] = captcha
    view_info['anon_captcha_base64'] = base64.standard_b64encode(captcha)
    user_id = auth_user.get_user_id()
    req = request.vars
    if req.form_submitted:
        if req.send_b:
            if req.subject and req.message:
                if auth_user.is_auth() or (
                    not auth_user.is_auth() and base64.standard_b64encode(
                        req.captcha_response) == req.c):
                    db.zf_admin_messages.insert(user_id=user_id,
                        subject=parse_content(req.subject),
                        message=parse_content(req.message),
                        creation_date=request.now,
                        read_flag=False)
                    redirect(URL(r=request, c='default', f='index'))
                else:
                    view_info['errors'].append('Invalid humanity challenge '
                                               'response, please try again')
                    return dict(request=request, view_info=view_info)
            else:
                view_info['errors'].append('Both Subject and Message are '
                                           'required fields')
                return dict(request=request, view_info=view_info)
        else:
            redirect(URL(r=request, c='default', f='index'))
    else:
        return dict(request=request, view_info=view_info)

def unauthorized():
    return dict()

def invalid_request():
    return dict()

def search():
    search_str = request.vars.search_str.strip().lower()
    results = []
    view_info = {}
    view_info['errors'] = []
    if len(search_str) >= 3:
        search_str = '%%%s%%' % (search_str)
        results = db(((
            (db.zf_topic.title.lower().like(search_str)) &
            (db.zf_topic.parent_flag==True)) |
            (db.zf_topic.content.lower().like(search_str))) &
            (db.zf_topic.disabled_flag==False) &
            (db.zf_forum.id==db.zf_topic.forum_id)).select(
            db.zf_topic.ALL, db.zf_forum.forum_title,
            orderby=~db.zf_topic.modifying_date, limitby=(0, 100))
    else:
        view_info['errors'].append('Search string must be three or more '
                                   'characters')
    return dict(request=request, search_str=request.vars.search_str,
                results=results, view_info=view_info)

@auth_user.requires_login()
def preferences():
    view_info = {}
    view_info['errors'] = []
    view_info['props'] = {}
    req = request.vars
    user_id = auth_user.get_user_id()
    # Avatar Restrictions (px) - Maybe we need to make these dynamic??
    AVATAR_MAX_HEIGHT = 100
    AVATAR_MAX_WIDTH  = 120
    AVATAR_MAX_SIZE   = 15000 # Bytes
    user_email = db(db.auth_users.id == user_id).select(
        db.auth_users.auth_email)[0].auth_email
    view_info['props'].update({'real_name':
        forumhelper.get_member_property('zfmp_real_name', user_id, '')})
    view_info['props'].update({'web_page':
        forumhelper.get_member_property('zfmp_web_page', user_id, '')})
    view_info['props'].update({'country':
        forumhelper.get_member_property('zfmp_country', user_id, '')})
    view_info['props'].update({'signature':
        forumhelper.get_member_property('zfmp_signature', user_id, '')})
    view_info['props'].update({'locale':
        forumhelper.get_member_property('zfmp_locale', user_id, '')})
    view_info['props'].update({'allow_pm_use':
        forumhelper.get_member_property('zfmp_allow_pm_use', user_id, '')})
    view_info['props'].update({'postings':
        forumhelper.get_member_property('zfmp_postings', user_id, '0')})
    view_info['props'].update({'last_login':
        forumhelper.get_member_property(
            'zfmp_last_login', user_id, str(XML(T('Never'))))})
    view_info['props'].update({'username':
        forumhelper.get_member_property(
            'zfmp_display_name', user_id, 'user_%s' % (user_id))})
    forum_subscriptions = db((db.zf_member_subscriptions.user_id == user_id) &
        (db.zf_member_subscriptions.subscription_type == 'F') &
        (db.zf_member_subscriptions.subscription_id == db.zf_forum.id) &
        (db.zf_member_subscriptions.subscription_active == True)).select(
        db.zf_forum.id, db.zf_forum.forum_title)
    topic_subscriptions = db((db.zf_member_subscriptions.user_id == user_id) &
        (db.zf_member_subscriptions.subscription_type == 'T') &
        (db.zf_member_subscriptions.subscription_id == db.zf_topic.id) &
        (db.zf_member_subscriptions.subscription_active == True)).select(
        db.zf_topic.id, db.zf_topic.title)
    available_languages = db(db.zf_available_languages.enabled == True).select(
        db.zf_available_languages.ALL,
        orderby=db.zf_available_languages.language_desc)

    if req.form_submitted:
        if req.update_b:
            # Standard Properties
            forumhelper.put_member_property('zfmp_real_name', user_id,
                                            req.real_name)
            forumhelper.put_member_property('zfmp_web_page', user_id,
                                            req.web_page)
            forumhelper.put_member_property('zfmp_country', user_id,
                                            req.country)
            forumhelper.put_member_property('zfmp_signature', user_id,
                                            req.signature)
            forumhelper.put_member_property('zfmp_locale', user_id,
                                            req.locale)
            if req.allow_pm_use:
                zfmp_allow_pm_use = "1"
            else:
                zfmp_allow_pm_use = ""
            forumhelper.put_member_property('zfmp_allow_pm_use', user_id,
                                            zfmp_allow_pm_use)

            # "Username" is a new member property called 'zfmp_display_name'
            # Which is only an identifier for the user, which they can change,
            # however, there cannot be two users with the same name, so
            # if the username is taken, notify the user to change it, or
            # use the default of "user_[id]"
            username = req.username.strip()
            if username:
                # Check if this username is already taken... and that
                # user is (obviously) not yourself
                if db(
                    (db.zf_member_properties.property_value.lower() == \
                     username.lower()) &
                    (db.zf_member_properties.property_id == \
                     db.zf_member_properties_skel.id) &
                    (db.zf_member_properties_skel.property_name == \
                     'zfmp_display_name') &
                    (db.zf_member_properties.user_id != user_id)).count():
                        view_info['errors'].append('This username already '
                                                   'exists, please choose '
                                                   'another one')
                else:
                    # Nope, does not exist, update..
                    forumhelper.put_member_property('zfmp_display_name',
                                                    user_id, username)
            else:
                view_info['errors'].append('The Username value cannot be '
                                           'empty')

            # Topic Subscriptions
            remove_topic_subscription = req.remove_topic_subscription
            if remove_topic_subscription:
                if type(remove_topic_subscription) == type([]):
                    for topic_id in remove_topic_subscription:
                        forumhelper.del_topic_subscription(int(topic_id),
                                                           user_id)
                else:
                    forumhelper.del_topic_subscription(
                        int(remove_topic_subscription), user_id)

            # Forum Subscriptions
            remove_forum_subscription = req.remove_forum_subscription
            if remove_forum_subscription:
                if type(remove_forum_subscription) == type([]):
                    for forum_id in remove_forum_subscription:
                        forumhelper.del_forum_subscription(int(forum_id),
                                                           user_id)
                else:
                    forumhelper.del_forum_subscription(
                        int(remove_forum_subscription), user_id)

            # Password Changes
            if req.new_passwd or req.new_passwd_confirm:
                if req.new_passwd == req.new_passwd_confirm:
                    hash_passwd = hashlib.sha1(
                        auth_user.get_user_name() + req.new_passwd).hexdigest()
                    db(db.auth_users.id == user_id).update(
                        auth_passwd=hash_passwd)
                else:
                    view_info['errors'].append('Password and confirmation do '
                                               'not match, please try again')

            # Avatars
            if req.remove_avatar:
                db(db.zf_member_avatars.user_id == user_id).update(
                    avatar_active=False)

            # Selected Language (allow storing the "default"
            # value (an empty string))
            forumhelper.put_member_property('zfmp_locale', user_id,
                                            req.lang_code)

            # Crude verification of a FileUpload object set
            try:
                filename = req.avatar_data.filename
            except AttributeError:
                filename = ''

            if filename:
                # Resource: http://epydoc.sourceforge.net/stdlib/cgi.
                # FieldStorage-class.html
                image_data = req.avatar_data.file.read()
                content_type = req.avatar_data.type # "image/png"
                doc_type, ext = content_type.split('/')
                if doc_type == 'image':
                    c_type, width, height = forumhelper.get_image_info(
                        image_data)
                    update_avatar = True
                    if height > AVATAR_MAX_HEIGHT or width > AVATAR_MAX_WIDTH:
                        view_info['errors'].append('Image dimensions exceed '
                                                   'the limits set by the '
                                                   'administrator: (H:'
                                                   '%spx, W:%spx)' % (height,
                                                                      width))
                        update_avatar = False
                    if len(image_data) > AVATAR_MAX_SIZE:
                        view_info['errors'].append('Avatar exceeds the '
                                                   'maximum image size set by '
                                                   'the administrator: '
                                                   '%s bytes' % (
                                                    len(image_data)))
                        update_avatar = False

                    if update_avatar:
                        if forumhelper.has_member_avatar(user_id,
                                                         bypass=False):
                            # Update:
                            db(db.zf_member_avatars.user_id==user_id).update(
                                content_type=content_type,
                                avatar_image=image_data, avatar_active=True)
                        else:
                            # Add:
                            db.zf_member_avatars.insert(
                                content_type=content_type,
                                user_id=user_id,
                                avatar_image=image_data, avatar_active=True)

            if view_info['errors']:
                return dict(request=request, view_info=view_info,
                            user_id=user_id, user_email=user_email,
                            forum_subscriptions=forum_subscriptions,
                            topic_subscriptions=topic_subscriptions,
                            available_languages=available_languages)
            else:
                redirect(URL(r=request, c='default', f='preferences',
                             vars=dict(lang=req.lang_code, upd=1)))
        else:
            redirect(URL(r=request, c='default', f='index'))
    else:
        return dict(request=request, view_info=view_info, user_id=user_id,
                    user_email=user_email,
                    forum_subscriptions=forum_subscriptions,
                    topic_subscriptions=topic_subscriptions,
                    available_languages=available_languages)


def get_avatar_image():
    auth_user = request.args[0]
    avatar_info = db(db.zf_member_avatars.auth_user==auth_user).select(
        db.zf_member_avatars.content_type, db.zf_member_avatars.avatar_image)
    response.headers['Content-Type'] = '%s' % (avatar_info[0].content_type)
    return avatar_info[0].avatar_image
