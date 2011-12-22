import hashlib
import random

@auth_user.requires_role('zAdministrator')
def index():
    cat_cnt = db.zf_forum_category.id.count()
    categories = db().select(cat_cnt)[0]._extra[cat_cnt]

    forum_cnt = db.zf_forum.id.count()
    forums = db().select(forum_cnt)[0]._extra[forum_cnt]

    topics = db(db.zf_topic.parent_flag==True).count()

    responses = db(db.zf_topic.parent_flag==False).count()

    views_sum = db.zf_topic.hits.sum()
    views = db(db.zf_topic.parent_flag==True).select(
        views_sum)[0]._extra[views_sum] or 0

    member_cnt = db.auth_users.id.count()
    members = db().select(member_cnt)[0]._extra[member_cnt]
    return dict(request=request, categories=categories, forums=forums,
                topics=topics, responses=responses, views=views,
                members=members)

@auth_user.requires_role('zAdministrator')
def categories():
    view_info = {}
    view_info['errors'] = []
    re_read = False
    req = request.vars
    categories = db().select(db.zf_forum_category.ALL,
                             orderby=db.zf_forum_category.cat_sort)
    if req.form_submitted:
        if req.save_sort:
            # Saving sorting requested
            for cat in categories:
                cat_id = cat.id
                if req.has_key('cat_id_%s' % (cat_id)):
                    try:
                        new_cat_sort = int(req['cat_id_%s' % (cat_id)])
                        save_sort = True
                    except ValueError:
                        view_info['errors'].append('%s %s' % (
                            XML(T('Invalid Sort Order value for')),
                            cat.cat_name))
                        save_sort = False
                    if save_sort:
                        re_read = True
                        db(db.zf_forum_category.id==cat_id).update(
                            cat_sort=new_cat_sort)
            view_info['sort_saved'] = 1
        else:
            # Add new category requested
            redirect(URL(r=request, c='zadmin', f='add_category'))
    if re_read:
        categories = db().select(db.zf_forum_category.ALL,
                                 orderby=db.zf_forum_category.cat_sort)
    return dict(request=request, categories=categories, view_info=view_info)

@auth_user.requires_role('zAdministrator')
def add_category():
    view_info = {}
    view_info['errors'] = []
    req = request.vars
    if req.form_submitted:
        if req.add_cat:
            cat_name = req.cat_name
            cat_desc = req.cat_desc or ''
            cat_visible_list = []
            zmember_access = req.zmember_access
            zmember_vip_access = req.zmember_vip_access
            if not cat_name: # and cat_desc):
                view_info['errors'].append(XML(T('Category name is a required '
                                                 'field')))
            if view_info['errors']:
                return dict(request=request, view_info=view_info)
            else:
                if req.zadmin_access:
                    cat_visible_to = 'zAdministrator'
                elif req.auth_access:
                    cat_visible_to = 'Authenticated'
                elif req.public_access:
                    cat_visible_to = ''
                else:
                    if zmember_access:
                        cat_visible_list.append('zMember')
                    if zmember_vip_access:
                        cat_visible_list.append('zMemberVIP')
                    cat_visible_to = ','.join(cat_visible_list)
                # Add Category Here
                db.zf_forum_category.insert(cat_name=cat_name,
                                            cat_desc=cat_desc,
                                            cat_visible_to=cat_visible_to)
                redirect(URL(r=request, c='zadmin', f='categories'))
        else:
            redirect(URL(r=request, c='zadmin', f='categories'))
    else:
        return dict(request=request, view_info=view_info)

@auth_user.requires_role('zAdministrator')
def edit_category():
    view_info = {}
    view_info['errors'] = []
    req = request.vars
    if req.form_submitted:
        if req.update_cat:
            cat_id = int(req.cat_id)
            this_category = db(db.zf_forum_category.id==cat_id).select(
                db.zf_forum_category.ALL)[0]
            cat_name = req.cat_name
            cat_desc = req.cat_desc or ''
            cat_visible_list = []
            zmember_access = req.zmember_access
            zmember_vip_access = req.zmember_vip_access
            if not cat_name: # and cat_desc):
                view_info['errors'].append(XML(T('Category name is a required '
                                                 'field')))
            if view_info['errors']:
                return dict(request=request, view_info=view_info,
                            this_category=this_category)
            else:
                if req.zadmin_access:
                    cat_visible_to = 'zAdministrator'
                elif req.auth_access:
                    cat_visible_to = 'Authenticated'
                elif req.public_access:
                    cat_visible_to = ''
                else:
                    if zmember_access:
                        cat_visible_list.append('zMember')
                    if zmember_vip_access:
                        cat_visible_list.append('zMemberVIP')
                    cat_visible_to = ','.join(cat_visible_list)
                # Add Category Here
                db(db.zf_forum_category.id == cat_id).update(
                    cat_name=cat_name,
                    cat_desc=cat_desc,
                    cat_visible_to=cat_visible_to)
                redirect(URL(r=request, c='zadmin', f='categories'))
        elif req.remove:
            # User has requested to remove an entire category, if the category
            # is empty, remove it immediately, otherwise send it to a page
            # where the user can move the forums associated to the category
            # to other category.
            cat_id = int(req.cat_id)
            #sql = "select count(*) from zf_forum where cat_id = %s" % (cat_id)
            forums_in_cat = db(db.zf_forum.id==cat_id).count()
            if forums_in_cat > 0:
                redirect(URL(r=request, c='zadmin', f='del_category',
                             args=[cat_id]))
            else:
                db(db.zf_forum_category.id==cat_id).delete()
                redirect(URL(r=request, c='zadmin', f='categories'))
        else:
            redirect(URL(r=request, c='zadmin', f='categories'))
    else:
        cat_id = int(request.args[0])
        this_category = db(db.zf_forum_category.id==cat_id).select(
            db.zf_forum_category.ALL)[0]
        return dict(request=request, view_info=view_info,
                    this_category=this_category)


@auth_user.requires_role('zAdministrator')
def forums():
    """ Main forums display page, basically show every forum for a
    specific category and display the forum's properties

    """
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    cat_forums = []
    selected_category = []
    selected_cat_id = 0
    cats = db().select(db.zf_forum_category.ALL,
                       orderby=db.zf_forum_category.cat_name)
    if req.form_submitted:
        # There can be only two options here: Save Sort or Add new Forum,
        # the first one saves all here, the secon one is a redirect
        cat_id = int(req.cat_id)
        if req.save_sort:
            re_read = False
            cat_forums = db(db.zf_forum.cat_id==cat_id).select(
                db.zf_forum.ALL,
                orderby=db.zf_forum.forum_sort)
            for forum in cat_forums:
                if req.has_key('forum_id_%s' % (forum.id)):
                    try:
                        forum_id_sort_value = int(
                            req['forum_id_%s' % (forum.id)])
                        save_sort = True
                    except ValueError:
                        view_info['errors'].append('%s %s' % (
                            XML(T('Invalid sorting value for forum')),
                            forum.forum_title))
                        save_sort = False
                    if save_sort:
                        re_read = True
                        db(db.zf_forum.id==forum.id).update(
                            forum_sort=forum_id_sort_value)
                        view_info['sort_saved'] = 1
            if re_read:
                cat_forums = db(db.zf_forum.cat_id==cat_id).select(
                    db.zf_forum.ALL, orderby=db.zf_forum.forum_sort)

            selected_category = db(db.zf_forum_category.id==cat_id).select(
                db.zf_forum_category.ALL)[0]
            return dict(request=request, selected_category=selected_category,
                        cat_forums=cat_forums, view_info=view_info, cats=cats)
        else:
            # User Picked "Add New Forum"
            redirect(URL(r=request, c='zadmin', f='add_forum', args=[cat_id]))
    else:
        # Entering for the first time, or the use switched categories using
        # the provided selection widget
        if len(request.args):
            selected_cat_id = int(request.args[0])
            for cat in cats:
                if cat.id == selected_cat_id:
                    selected_category = cat
                    break
        else:
            # No category is selected, attempt to grab the first one found
            if len(cats):
                selected_category = cats[0]
                selected_cat_id = selected_category.id

        if len(selected_category):
            # Ok, a category has been selected, grab the category's forums
            cat_forums = db(db.zf_forum.cat_id==selected_cat_id).select(
                db.zf_forum.ALL, orderby=db.zf_forum.forum_sort)

        return dict(request=request, selected_category=selected_category,
                    cat_forums=cat_forums, view_info=view_info, cats=cats)

@auth_user.requires_role('zAdministrator')
def add_forum():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    cats = db().select(db.zf_forum_category.ALL,
                       orderby=db.zf_forum_category.cat_name)
    if req.form_submitted:
        cat_id = int(req.new_cat_id) # Always available
        if req.add_forum:
            # Check Required fields first
            if req.title and req.description:
                add_postings_access_roles_list = []
                reply_postings_access_roles_list = []

                # Topic Creation Access Level
                if req.zadmin_add:
                    add_postings_access_roles = 'zAdministrator'
                elif req.auth_add:
                    add_postings_access_roles = 'Authenticated'
                elif req.public_add:
                    add_postings_access_roles = ''
                else:
                    if req.zmember_add:
                        add_postings_access_roles_list.append('zMember')
                    if req.zmember_vip_add:
                        add_postings_access_roles_list.append('zMemberVIP')
                    add_postings_access_roles = ','.join(
                        add_postings_access_roles_list)

                # Topic Reply Access Level
                if req.zadmin_reply:
                    reply_postings_access_roles = 'zAdministrator'
                elif req.auth_reply:
                    reply_postings_access_roles = 'Authenticated'
                elif req.public_reply:
                    reply_postings_access_roles = ''
                else:
                    if req.zmember_reply:
                        reply_postings_access_roles_list.append('zMember')
                    if req.zmember_vip_reply:
                        reply_postings_access_roles_list.append('zMemberVIP')
                    reply_postings_access_roles = ','.join(
                        reply_postings_access_roles_list)

                # Will this forum be moderated?
                if req.moderated_forum:
                    moderation_flag = True
                else:
                    moderation_flag = False

                # Will Anonymous be able to browse the forum?
                if req.anonymous_view:
                    anonymous_viewaccess = True
                else:
                    anonymous_viewaccess = False

                # Will topics in this forum be displayed in the "
                # latest Topic" section in the leftnav
                if req.latest_topics:
                    include_latest_topics = True
                else:
                    include_latest_topics = False

                # Insert the record and go back
                db.zf_forum.insert(cat_id=cat_id,
                    forum_title=req.title,
                    forum_desc=req.description,
                    moderation_flag=moderation_flag,
                    anonymous_viewaccess=anonymous_viewaccess,
                    add_postings_access_roles=add_postings_access_roles,
                    reply_postings_access_roles=reply_postings_access_roles,
                    include_latest_topics=include_latest_topics)
                redirect(URL(r=request, c='zadmin', f='forums', args=[cat_id]))

            else:
                view_info['errors'].append(
                    XML(T('Both forum title and description are required '
                          'fields')))
                selected_category = db(
                    db.zf_forum_category.id==cat_id).select()[0]
                return dict(request=request,
                            selected_category=selected_category,
                            cats=cats, view_info=view_info)
        else:
            # Back to forums
            redirect(URL(r=request, c='zadmin', f='forums', args=[cat_id]))
    else:
        cat_id = int(request.args[0])
        selected_category = db(db.zf_forum_category.id==cat_id).select()[0]
        return dict(request=request, selected_category=selected_category,
                    cats=cats, view_info=view_info)


@auth_user.requires_role('zAdministrator')
def edit_forum():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    cats = db().select(db.zf_forum_category.ALL,
                       orderby=db.zf_forum_category.cat_name)
    if req.form_submitted:
        cat_id = int(req.new_cat_id)
        if req.update_forum:
            # Check Required fields first
            if req.title and req.description:
                forum_id = int(req.forum_id)
                add_postings_access_roles_list = []
                reply_postings_access_roles_list = []

                # Topic Creation Access Level
                if req.zadmin_add:
                    add_postings_access_roles = 'zAdministrator'
                elif req.auth_add:
                    add_postings_access_roles = 'Authenticated'
                elif req.public_add:
                    add_postings_access_roles = ''
                else:
                    if req.zmember_add:
                        add_postings_access_roles_list.append('zMember')
                    if req.zmember_vip_add:
                        add_postings_access_roles_list.append('zMemberVIP')
                    add_postings_access_roles = ','.join(
                        add_postings_access_roles_list)

                # Topic Reply Access Level
                if req.zadmin_reply:
                    reply_postings_access_roles = 'zAdministrator'
                elif req.auth_reply:
                    reply_postings_access_roles = 'Authenticated'
                elif req.public_reply:
                    reply_postings_access_roles = ''
                else:
                    if req.zmember_reply:
                        reply_postings_access_roles_list.append('zMember')
                    if req.zmember_vip_reply:
                        reply_postings_access_roles_list.append('zMemberVIP')
                    reply_postings_access_roles = ','.join(
                        reply_postings_access_roles_list)

                # Will this forum be moderated?
                if req.moderated_forum:
                    moderation_flag = True
                else:
                    moderation_flag = False

                # Will Anonymous be able to browse the forum?
                if req.anonymous_view:
                    anonymous_viewaccess = True
                else:
                    anonymous_viewaccess = False

                # Will topics in this forum be displayed in the "
                # latest Topic" section in the leftnav
                if req.latest_topics:
                    include_latest_topics = True
                else:
                    include_latest_topics = False

                # Update the record and go back
                db(db.zf_forum.id==forum_id).update(cat_id=cat_id,
                    forum_title=req.title,
                    forum_desc=req.description,
                    moderation_flag=moderation_flag,
                    anonymous_viewaccess=anonymous_viewaccess,
                    add_postings_access_roles=add_postings_access_roles,
                    reply_postings_access_roles=reply_postings_access_roles,
                    include_latest_topics=include_latest_topics)
                redirect(URL(r=request, c='zadmin', f='forums', args=[cat_id]))
        else:
            # Back to forums
            redirect(URL(r=request, c='zadmin', f='forums', args=[cat_id]))
    else:
        forum_id = int(request.args[0])
        this_forum = db(db.zf_forum.id==forum_id).select()[0]
        return dict(request=request, view_info=view_info,
                    this_forum=this_forum,
                    cats=cats)

@auth_user.requires_role('zAdministrator')
def system_config():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    system_properties = forumhelper.get_system_properties()
    if req.form_submitted:
        if req.save_sys_params:
            for req_var in req:
                    if req_var[:16] == 'new_property_id_':
                        property_id = int(req[req_var])
                        new_property_value = req['new_property_value_%s' % (property_id)]
                        db(db.zf_system_properties.id==property_id).update(
                            property_value=new_property_value)
                        view_info.update({'updated': True})

    system_properties = forumhelper.get_system_properties()
    return dict(request=request, system_properties=system_properties,
                view_info=view_info)

@auth_user.requires_role('zAdministrator')
def bad_topics():
    """ Manage Inappropriate topics """
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    tot_del = 0
    if req.form_submitted:
        for item in req:
            if item[:9] == 'inapp_id_':
                inapp_id = int(req[item])
                db(db.zf_topic_inappropriate.id==inapp_id).update(read_flag=True)
                tot_del += 1
        topics = db((db.zf_topic_inappropriate.read_flag==False) & (db.zf_topic.id==db.zf_topic_inappropriate.topic_id)).select(db.zf_topic_inappropriate.ALL, db.zf_topic.title, orderby=~db.zf_topic_inappropriate.creation_date)
        view_info.update({'removed': tot_del})
        return dict(request=request, topics=topics, view_info=view_info)
    else:
        topics = db((db.zf_topic_inappropriate.read_flag==False) & (db.zf_topic.id==db.zf_topic_inappropriate.topic_id)).select(db.zf_topic_inappropriate.ALL, db.zf_topic.title, orderby=~db.zf_topic_inappropriate.creation_date)
        return dict(request=request, topics=topics, view_info=view_info)

@auth_user.requires_role('zAdministrator')
def admin_msgs():
    """ Manage Admin Messages """
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    tot_del = 0
    if req.form_submitted:
        if req.read_b:
            for item in req:
                if item[:7] == 'msg_id_':
                    msg_id = int(req[item])
                    db(db.zf_admin_messages.id==msg_id).update(read_flag=True)
                    tot_del += 1
            messages = db(db.zf_admin_messages.read_flag==False).select(db.zf_admin_messages.ALL, orderby=~db.zf_admin_messages.creation_date)
            view_info.update({'removed': tot_del})
        elif req.purge_b:
            db(db.zf_admin_messages.read_flag == True).delete()
            messages = db(db.zf_admin_messages.read_flag==False).select(db.zf_admin_messages.ALL, orderby=~db.zf_admin_messages.creation_date)
        view_info['purge'] = db(db.zf_admin_messages.read_flag == True).count()
        return dict(request=request, messages=messages, view_info=view_info)
    else:
        view_info['purge'] = db(db.zf_admin_messages.read_flag == True).count()
        messages = db(db.zf_admin_messages.read_flag==False).select(db.zf_admin_messages.ALL, orderby=~db.zf_admin_messages.creation_date)
        return dict(request=request, messages=messages, view_info=view_info)

@auth_user.requires_role('zAdministrator')
def users():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    view_info['users'] = {}
    list_order = ~db.auth_users.is_enabled | ~db.auth_users.auth_created_on
    all_users = db().select(db.auth_users.ALL, orderby=list_order)
    for this_user in all_users:
        user_id = this_user.id
        #auth_email = this_user.auth_email
        user_posts = db((db.zf_topic.creation_user_id == user_id) &
            (db.zf_topic.parent_flag==True)).count()
        user_replies = db((db.zf_topic.creation_user_id == user_id) &
            (db.zf_topic.parent_flag==False)).count()
        sql_roles = db((db.auth_user_role.auth_user_id == user_id) &
            (db.auth_roles.id==db.auth_user_role.auth_role_id)).select(
            db.auth_roles.auth_role_name)
        user_roles = ','.join([auth_role_name.auth_role_name \
                               for auth_role_name in sql_roles])
        view_info['users'].update(
            {user_id: {'roles': user_roles,
                          'posts': user_posts,
                          'replies': user_replies,
                          'join_date': this_user.auth_created_on}})
    return dict(request=request, users=all_users, view_info=view_info)

@auth_user.requires_role('zAdministrator')
def user_edit():
    req = request.vars
    view_info = {}
    view_info['errors'] = []
    view_info['props'] = {}
    # Avatar Restrictions (px) - Maybe we need to make these dynamic??
    AVATAR_MAX_HEIGHT = 100
    AVATAR_MAX_WIDTH  = 120
    AVATAR_MAX_SIZE   = 15000 # Bytes
    available_roles = db().select(db.auth_roles.ALL,
                                  orderby=db.auth_roles.auth_role_name)
    view_info.update({'available_roles': available_roles})
    if req.form_submitted:
        user_id = req.user_id
    else:
        user_id = request.args[0]

    user_curr_role_id = db(
        (db.auth_users.id == user_id) &
        (db.auth_users.id == db.auth_user_role.auth_user_id)).select(
        db.auth_user_role.auth_role_id)[0].auth_role_id
    view_info.update({'current_role_id': user_curr_role_id})

    enabled_user = db(
        (db.auth_users.id == user_id) & \
        (db.auth_users.is_enabled == True)).count()
    user_email = db(db.auth_users.id == user_id).select(
        db.auth_users.auth_email)[0].auth_email
    view_info['props'].update({'real_name': forumhelper.get_member_property(
        'zfmp_real_name', user_id, '')})
    view_info['props'].update({'web_page': forumhelper.get_member_property(
        'zfmp_web_page', user_id, '')})
    view_info['props'].update({'country': forumhelper.get_member_property(
        'zfmp_country', user_id, '')})
    view_info['props'].update({'signature': forumhelper.get_member_property(
        'zfmp_signature', user_id, '')})
    view_info['props'].update({'locale': forumhelper.get_member_property(
        'zfmp_locale', user_id, '')})
    view_info['props'].update({'allow_pm_use': forumhelper.get_member_property(
        'zfmp_allow_pm_use', user_id, '')})
    view_info['props'].update({'postings': forumhelper.get_member_property(
        'zfmp_postings', user_id, '0')})
    view_info['props'].update({'last_login': forumhelper.get_member_property(
        'zfmp_last_login', user_id, str(XML(T('Never'))))})
    view_info['props'].update({'is_enabled': enabled_user})
    view_info['props'].update({'username':
        forumhelper.get_member_property(
            'zfmp_display_name', user_id, 'user_%s' % (user_id))})
    forum_subscriptions = db((
        db.zf_member_subscriptions.user_id == user_id) &
        (db.zf_member_subscriptions.subscription_type=='F') &
        (db.zf_member_subscriptions.subscription_id == db.zf_forum.id) &
        (db.zf_member_subscriptions.subscription_active == True)).select(
        db.zf_forum.id, db.zf_forum.forum_title)
    topic_subscriptions = db(
        (db.zf_member_subscriptions.user_id == user_id) &
        (db.zf_member_subscriptions.subscription_type == 'T') &
        (db.zf_member_subscriptions.subscription_id == db.zf_topic.id) &
        (db.zf_member_subscriptions.subscription_active == True)).select(
        db.zf_topic.id, db.zf_topic.title)
    available_languages = db(db.zf_available_languages.enabled == True).select(
        db.zf_available_languages.ALL,
        orderby=db.zf_available_languages.language_desc)

    if req.form_submitted:
        if req.update_b:
            # User's new role
            new_role = int(req.new_role)
            if (new_role != user_curr_role_id):
                # Only change role if it was modified
                user_id = db(db.auth_users.id == user_id).select(
                    db.auth_users.id)[0].id
                db(db.auth_user_role.auth_user_id == user_id).update(
                    auth_role_id=new_role)

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

            # Topic Subscriptions
            remove_topic_subscription = req.remove_topic_subscription
            if remove_topic_subscription:
                if type(remove_topic_subscription) == type([]):
                    for topic_id in remove_topic_subscription:
                        forumhelper.del_topic_subscription(
                            int(topic_id), user_id)
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
            if req.new_passwd:
                if req.new_passwd == req.new_passwd_confirm:
                    hash_passwd = hashlib.sha1(
                        auth_user.get_user_name() + req.new_passwd).hexdigest()
                    db(db.auth_users.id == user_id).update(
                        auth_passwd=hash_passwd)

            # Avatars
            if req.remove_avatar:
                db(db.zf_member_avatars.user_id == user_id).update(
                    avatar_active=False)
            try:
                filename = req.avatar_data.filename
            except AttributeError:
                filename = ''

            if filename:
                # http://epydoc.sourceforge.net/stdlib/
                # (cont'd) cgi.FieldStorage-class.html
                image_data = req.avatar_data.file.read()
                content_type = req.avatar_data.type # "image/png"
                doc_type, ext = content_type.split('/')
                if doc_type == 'image':
                    c_type, width, height = forumhelper.get_image_info(
                        image_data)
                    if height > AVATAR_MAX_HEIGHT or width > AVATAR_MAX_WIDTH:
                        view_info['errors'].append('Image dimensions exceed '
                                                   'the limits set by the '
                                                   'administrator: (H:%spx, '
                                                   'W:%spx)' % (height, width))
                    if len(image_data) > AVATAR_MAX_SIZE:
                        view_info['errors'].append('Avatar exceeds the '
                                                   'maximum '
                                                   'image size set by the '
                                                   'administrator: %s '
                                                   'bytes' % (len(image_data)))

                    if len(view_info['errors']):
                        raise ValueError, view_info['errors']
                    if not view_info['errors']:
                        #raise ValueError, (c_type, width, height,)
                        if forumhelper.has_member_avatar(user_id,
                                                         bypass=False):
                            # Update:
                            db(db.zf_member_avatars.user_id == \
                               user_id).update(content_type=content_type,
                                               avatar_image=image_data,
                                               avatar_active=True)
                        else:
                            # Add:
                            db.zf_member_avatars.insert(
                                content_type=content_type,
                                user_id=user_id,
                                avatar_image=image_data,
                                avatar_active=True)

            redirect(URL(r=request, c='zadmin', f='users'))
        elif req.disable_b:
            # Disabling: set the disabled flag on,
            # and change the user's password
            hash_passwd = hashlib.sha1(str(random.random())[2:]).hexdigest()
            db(db.auth_users.id == user_id).update(
                auth_passwd=hash_passwd, is_enabled=False)
            redirect(URL(r=request, c='zadmin', f='users'))
        elif req.enable_b:
            # Password defaults to email
            hash_passwd = hashlib.sha1(user_email + user_email).hexdigest()
            db(db.auth_users.id == user_id).update(
                auth_passwd=hash_passwd, is_enabled=True)
            redirect(URL(r=request, c='zadmin', f='users'))
        else:
            redirect(URL(r=request, c='zadmin', f='users'))
    else:
        return dict(request=request,
                    view_info=view_info,
                    user_email=user_email,
                    user_id=user_id,
                    forum_subscriptions=forum_subscriptions,
                    topic_subscriptions=topic_subscriptions,
                    available_languages=available_languages)

def get_avatar_image():
    auth_user = request.args[0]
    avatar_info = db(db.zf_member_avatars.auth_user==auth_user).select(
        db.zf_member_avatars.content_type, db.zf_member_avatars.avatar_image)
    response.headers['Content-Type'] = '%s' % (avatar_info[0].content_type)
    return avatar_info[0].avatar_image
