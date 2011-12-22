import base64
import struct
import smtplib
from gluon.html import URL
import random
import hashlib
from cStringIO import StringIO
import math

class ForumHelper(object):
    """ Provides methods to deal with the forum's miscellaneous
    functions """

    def __init__(self, environment, db, auth_user):
        self.request = environment['request']
        self.response = environment['response']
        self.session = environment['session']
        self.cache = environment['cache']
        self.db = db
        self.auth_user = auth_user

    def get_system_property(self, property_name, default_value):
        """ Checks for a possible system property and returns its
        associated value if the property exists and its value is empty,
        it does also return the default value

        """
        prop = self.db(self.db.zf_system_properties.property_name == \
            property_name).select(self.db.zf_system_properties.id,
                                  self.db.zf_system_properties.property_desc,
                                  self.db.zf_system_properties.property_value)
        if prop:
            property_value = prop[0].property_value
        else:
            property_value = default_value
        return property_value

    def get_system_properties(self):
        """ Returns all of pyForum's system properties """
        return self.db().select(self.db.zf_system_properties.ALL)

    def put_system_property(self, property_name, new_value):
        """ UPDATES an existing property name if it does indeed
        exist, "new value" must always be a string,
        it returns a boolean value describing success in adding the property
        or failure when the prioperty could not be updated """
        prop = self.db(self.db.zf_system_properties.property_name == \
            property_name).select(self.db.zf_system_properties.id)
        if prop:
            prop_id = prop[0].id
            self.db(self.db.zf_system_properties.id == \
                    prop_id).update(property_value=new_value)
            updated = True
        else:
            updated = False
        return updated

    # !NEW FUNCTION: get_friend_status
    #     This takes in the active user's id and a target id and checks whether the active user
    #     has set the target user as a friend
    def get_friend_status(self, my_id, friend_id):
        friend = False
        friend_check = self.db((self.db.zf_friend_user.self_id==my_id) & (self.db.zf_friend_user.target_id==friend_id)).select()
        if len(friend_check):
            friend = True 
        return friend
    # !END FUNCTION CODE
        
    def get_member_property(self, property_name, user_id, default_value):
        """ Similar to get_system_property() but will handle member properties
        instead of system properties

        """
        user_property_value = default_value
        # First check if the property exists
        property_check = self.db(
            self.db.zf_member_properties_skel.property_name == \
            property_name).select(self.db.zf_member_properties_skel.id)
        if len(property_check):
            property_id = property_check[0].id
            # Now check if the user *has* this property in his profile
            user_prop = self.db((self.db.zf_member_properties.property_id == \
                property_id) & (self.db.zf_member_properties.user_id == \
                user_id)).select(self.db.zf_member_properties.property_value)
            if user_prop:
                user_property_value = user_prop[0].property_value
        return user_property_value

    # !NEW FUNCTION: get_member_property_hidden
    #     This function returns whether or not the specified member property should
    #     be hidden in the user's profile
    def get_member_property_hidden(self, property_name, user_id, default_value):
        user_property_hidden = default_value
        # First check if the property exists
        property_check = self.db(
            self.db.zf_member_properties_skel.property_name == \
            property_name).select(self.db.zf_member_properties_skel.id)
        if len(property_check):
            property_id = property_check[0].id
            # Now check if the user *has* this property in his profile
            user_prop = self.db((self.db.zf_member_properties.property_id == \
                property_id) & (self.db.zf_member_properties.user_id == \
                user_id)).select(self.db.zf_member_properties.property_value)
            if user_prop:
                # Now check if the user has this property hidden
                user_property_hidden = self.db((self.db.zf_member_properties.property_id == property_id) & (self.db.zf_member_properties.user_id == user_id)).select(self.db.zf_member_properties.profile_hidden)[0].profile_hidden
        return user_property_hidden
    # !END NEW FUNCTION

    def get_display_name(self, user_id=None, default=None):
        """ This method is a shortcut for calling get_member_property()
        with the apporpriate parameter. It will return the user's "forum"
        name, which can be anything the user chooses in his/her profile

        """
        if user_id is None:
            user_id = self.auth_user.get_user_id()

        if default is None:
            default = 'user_%s' % (user_id) # Kind of a convention only
        return self.get_member_property('zfmp_display_name', user_id, default)

    def put_member_property(self, property_name, user_id, new_value):
        errors = {'errors': ''}
        # Check if the property exists
        property_check = self.db(
            self.db.zf_member_properties_skel.property_name == \
                property_name).select(
            self.db.zf_member_properties_skel.id,
            self.db.zf_member_properties_skel.member_editable)
        if len(property_check):
            property_id = property_check[0].id
            curr_user_id = self.auth_user.get_user_id()
            #member_editable = property_check[0].member_editable
            if curr_user_id == user_id or self.auth_user.is_admin():
                # Does this property exists for the user?
                prop_exists = self.db(
                    (self.db.zf_member_properties.property_id == \
                     property_id) & \
                    (self.db.zf_member_properties.user_id == \
                     user_id)).select(self.db.zf_member_properties.id)
                if len(prop_exists):
                    # Yes, then update
                    self.db(
                        (self.db.zf_member_properties.property_id == \
                        property_id) & \
                        (self.db.zf_member_properties.user_id == \
                         user_id)).update(property_value=new_value, profile_hidden=False)
                else:
                    # Nope, Create
                    self.db.zf_member_properties.insert(
                        user_id=user_id,
                        property_id=property_id, property_value=new_value)
            else:
                errors.update({'errors':
                    'Not allowed to change this property'})
        else:
            errors.update({'errors': 'Member property name not found'})
        return errors
        
    # !NEW FUNCTION: put_member_property_hidden
    #     Sets the hidden value of the specified member property for a given user.
    #     Based on put_member_property.
    def put_member_property_hidden(self, property_name, user_id, new_value):
        errors = {'errors': ''}
        # Check if the property exists
        property_check = self.db(
            self.db.zf_member_properties_skel.property_name == \
                property_name).select(
            self.db.zf_member_properties_skel.id,
            self.db.zf_member_properties_skel.member_editable)
        if len(property_check):
            property_id = property_check[0].id
            curr_user_id = self.auth_user.get_user_id()
            #member_editable = property_check[0].member_editable
            if curr_user_id == user_id or self.auth_user.is_admin():
                # Does this property exists for the user?
                prop_exists = self.db(
                    (self.db.zf_member_properties.property_id == \
                     property_id) & \
                    (self.db.zf_member_properties.user_id == \
                     user_id)).select(self.db.zf_member_properties.id)
                if len(prop_exists):
                    # Yes, then update
                    self.db(
                        (self.db.zf_member_properties.property_id == \
                        property_id) & \
                        (self.db.zf_member_properties.user_id == \
                         user_id)).update(profile_hidden=new_value)
            else:
                errors.update({'errors':
                    'Not allowed to change this property'})
        else:
            errors.update({'errors': 'Member property name not found'})
        return errors
    # !END NEW FUNCTION

    def has_member_avatar(self, user_id, bypass=True):
        """ Tests if there is an avatar stored for the user, if bypass is
        True, it'll check for the avatar active flag

        """
        if bypass:
            avatar_info = self.db(\
                    (self.db.zf_member_avatars.user_id == user_id) &
                    (self.db.zf_member_avatars.avatar_active == \
                     True)).select(self.db.zf_member_avatars.content_type,
                                   self.db.zf_member_avatars.avatar_image)
        else:
            avatar_info = self.db(self.db.zf_member_avatars.user_id == \
                self.db.zf_member_avatars.user_id).select(
                self.db.zf_member_avatars.content_type,
                self.db.zf_member_avatars.avatar_image)
        if len(avatar_info):
            return True
        else:
            return False

    def has_forum_subscription(self, forum_id, user_id):
        """ Returns True if auth_user is subscribed to the requested forum,
        False otherwise

        """
        return self._has_subscription(forum_id, 'F', user_id)

    def has_topic_subscription(self, topic_id, user_id):
        """ Returns True if auth_user is subscribed to the requested topic,
        False otherwise

        """
        return self._has_subscription(topic_id, 'T', user_id)

    def _has_subscription(self, object_id, object_type, user_id):
        """ Returns True if auth_user is subscribed to the requested
        forum/topic, False otherwise

        """
        subscribed = False
        #raise ValueError, self.auth_user.is_auth()
        if user_id:
            if self.db(
                (self.db.zf_member_subscriptions.user_id == user_id) &
                (self.db.zf_member_subscriptions.subscription_type == \
                 object_type) &
                (self.db.zf_member_subscriptions.subscription_active == True) &
                (self.db.zf_member_subscriptions.subscription_id == \
                 object_id)).select(self.db.zf_member_subscriptions.id):
                subscribed = True
        return subscribed

    def add_topic_subscription(self, topic_id, user_id):
        """ Handles Topic Subscriptions """
        return self._handle_subscription(topic_id, 'T', user_id, 'add')

    def del_topic_subscription(self, topic_id, user_id):
        """ Handles Topic Subscriptions """
        return self._handle_subscription(topic_id, 'T', user_id, 'remove')

    def add_forum_subscription(self, forum_id, user_id):
        """ Handles Forum Subscriptions """
        return self._handle_subscription(forum_id, 'F', user_id, 'add')

    def del_forum_subscription(self, forum_id, user_id):
        """ Handles Forum Subscriptions """
        return self._handle_subscription(forum_id, 'F', user_id, 'remove')

    def _handle_subscription(self, object_id, object_type, user_id, action):
        """ object_id is a forum_id or a topic_id, object_type is "F" for
        forum, "T" for topic, action is "add" or "remove"

        """
        success = True
        # See if the record actually exists
        subscription = self.db(
            (self.db.zf_member_subscriptions.subscription_id == object_id) &
            (self.db.zf_member_subscriptions.user_id == user_id) &
            (self.db.zf_member_subscriptions.subscription_type == \
             object_type)).select()
        if len(subscription):
            # Ok, there is a record, this means that we'll update it rather
            # than add a new one
            if action == "add":
                self.db(
                    (self.db.zf_member_subscriptions.subscription_id == \
                     object_id) &
                    (self.db.zf_member_subscriptions.user_id == user_id) &
                    (self.db.zf_member_subscriptions.subscription_type == \
                     object_type)).update(subscription_active=True)
            elif action == "remove":
                self.db(
                    (self.db.zf_member_subscriptions.subscription_id == \
                     object_id) &
                    (self.db.zf_member_subscriptions.user_id == user_id) &
                    (self.db.zf_member_subscriptions.subscription_type == \
                     object_type)).update(subscription_active=False)
            else:
                success = False
        else:
            # No record found, add a brand new one, in this case there
            # can be no "remove"
            self.db.zf_member_subscriptions.insert(
                user_id=user_id,
                subscription_id=object_id,
                subscription_type=object_type,
                subscription_active=True)
        return success

    def get_user_rank(self, user_id):
        """ Returns the rank of the user """
        rank = ''
        hits = int(self.get_member_property('zfmp_postings', user_id, 0))
        rank_info = self.db(
            self.db.zf_member_rank.rank_value_min <= hits).select(
            self.db.zf_member_rank.rank_name,
            orderby=~self.db.zf_member_rank.rank_value_min, limitby=(0,1))
        #raise ValueError, rank_info
        if len(rank_info):
            rank = rank_info[0].rank_name
        return rank

    def get_system_announcements(self, include_content=False, rss=False):
        max_sys_announcements = int(
            self.get_system_property('zfsp_system_announcement_max', 0))
        sys_topics = None
        if max_sys_announcements:
            if include_content:
                sys_topics = self.db(
                    (self.db.zf_topic.system_announcement_flag == True) &
                    (self.db.zf_topic.parent_flag == True)).select(
                    self.db.zf_topic.title,
                    self.db.zf_topic.id,
                    self.db.zf_topic.modifying_date,
                    self.db.zf_topic.content,
                    orderby=~self.db.zf_topic.modifying_date,
                    limitby=(0, max_sys_announcements))
            else:
                sys_topics = self.db(
                    (self.db.zf_topic.system_announcement_flag == True) &
                    (self.db.zf_topic.parent_flag == True)).select(
                    self.db.zf_topic.title,
                    self.db.zf_topic.id,
                    self.db.zf_topic.modifying_date,
                    orderby=~self.db.zf_topic.modifying_date,
                    limitby=(0, max_sys_announcements))
            if not len(sys_topics) and not rss:
                sys_topics = [{'error':'No Topics'}]
        else:
            if not rss:
                sys_topics = [{'error':'No Topics'}]
        return sys_topics

    def get_latest_topics(self, include_content=False, rss=False):
        max_topics = int(
            self.get_system_property('zfsp_latest_postings_max', 0))
        latest_topics = None
        if max_topics:
            if include_content:
                latest_topics = self.db(\
                        (self.db.zf_topic.system_announcement_flag == False) &
                        (self.db.zf_forum.include_latest_topics == True) &
                        (self.db.zf_forum.id == self.db.zf_topic.forum_id) &
                        (self.db.zf_topic.parent_flag==True) \
                    ).select(self.db.zf_topic.title,
                        self.db.zf_topic.id,
                        self.db.zf_topic.modifying_date,
                        self.db.zf_topic.content,
                        orderby=~self.db.zf_topic.modifying_date,
                        limitby=(0, max_topics))
            else:
                latest_topics = self.db(
                    (self.db.zf_topic.system_announcement_flag == False) &
                    (self.db.zf_forum.include_latest_topics == True) &
                    (self.db.zf_forum.id == self.db.zf_topic.forum_id) &
                    (self.db.zf_topic.parent_flag == True)).select(
                    self.db.zf_topic.title,
                    self.db.zf_topic.id,
                    self.db.zf_topic.modifying_date,
                    orderby=~self.db.zf_topic.modifying_date,
                    limitby=(0, max_topics))
            if not len(latest_topics) and not rss:
                latest_topics = [{'error':'No Topics'}]
        else:
            if not rss:
                latest_topics = [{'error':'No Topics'}]
        return latest_topics

    def setup_notifications(self, subscription_id, subscription_type, now):
        """ subscription_id is the topic.id or forum.id being updated,
        subscription_type is 'T' (Topic) or 'F' (Forum)

        """
        # Grab all users subscribed to this object
        subscribers = self.db(
            (self.db.zf_member_subscriptions.subscription_active == True) &
            (self.db.zf_member_subscriptions.subscription_id == \
             subscription_id) &
            (self.db.zf_member_subscriptions.subscription_type == \
             subscription_type)).select(
            self.db.zf_member_subscriptions.user_id)
        if subscribers:
            for subscriber in subscribers:
                # Only add this subscription notification email request
                # if another one for the same type/object/validity does
                # not exist yet..
                is_subscribed = self.db(
                    (self.db.zf_member_subscriptions_notification.user_id == subscriber.user_id) &
                    (self.db.zf_member_subscriptions_notification.subscription_type == subscription_type) &
                    (self.db.zf_member_subscriptions_notification.subscription_id == subscription_id) &
                    (self.db.zf_member_subscriptions_notification.is_processed == False)).count() > 0
                if not is_subscribed:
                    self.db.zf_member_subscriptions_notification.insert(
                        user_id=subscriber.user_id,
                        subscription_id=subscription_id,
                        subscription_type=subscription_type,
                        creation_date=now,
                        is_processed=False)

    def get_inappropriate_topics_cnt(self):
        return self.db(self.db.zf_topic_inappropriate.read_flag ==\
                       False).count()

    def get_admin_msgs_cnt(self):
        return self.db(self.db.zf_admin_messages.read_flag == False).count()

    def get_my_messages_cnt(self):
        msg_count = self.db(
            (self.db.zf_pm.user_id == self.auth_user.get_user_id()) &
            (self.db.zf_pm.read_flag == False)).count()
        if msg_count > 0:
            rval = '<b style="color:red;">(%s)</b>' % (msg_count)
        else:
            rval = '(%s)' % (msg_count)
        return rval

    def get_image_info(self, data):
        data = str(data)
        size = len(data)
        height = -1
        width = -1
        content_type = ''

        # handle GIFs
        if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
            # Check to see if content_type is correct
            content_type = 'image/gif'
            w, h = struct.unpack("<HH", data[6:10])
            width = int(w)
            height = int(h)

        # See PNG v1.2 spec (http://www.cdrom.com/pub/png/spec/)
        # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
        # and finally the 4-byte width, height
        elif ((size >= 24) and (data[:8] == '\211PNG\r\n\032\n') and
            (data[12:16] == 'IHDR')):
            content_type = 'image/png'
            w, h = struct.unpack(">LL", data[16:24])
            width = int(w)
            height = int(h)

        # Maybe this is for an older PNG version.
        elif (size >= 16) and (data[:8] == '\211PNG\r\n\032\n'):
            # Check to see if we have the right content type
            content_type = 'image/png'
            w, h = struct.unpack(">LL", data[8:16])
            width = int(w)
            height = int(h)

        elif (size >= 2) and (data[:2] == '\377\330'):
            content_type = 'image/jpeg'
            jpeg = StringIO(data)
            jpeg.read(2)
            b = jpeg.read(1)
            try:
                while (b and ord(b) != 0xDA):
                    while (ord(b) != 0xFF):
                        b = jpeg.read(1)
                    while (ord(b) == 0xFF):
                        b = jpeg.read(1)
                    if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                        jpeg.read(3)
                        h, w = struct.unpack(">HH", jpeg.read(4))
                        break
                    else:
                        jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
                    b = jpeg.read(1)
                width = int(w)
                height = int(h)
            except:
                pass

        return content_type, width, height

    def gen_pwd(self):
        vowels='aeiou'
        consonants='bcdfghjklmnpqrstvwxyz'
        password=''
        # Some default values should be in the parameters section
        minpairs = 4
        maxpairs = 6

        for x in range(1, random.randint(int(minpairs), int(maxpairs))):
            consonant = consonants[random.randint(1, len(consonants) - 1)]
            if random.choice([1,0]):
                consonant = consonant.upper()
            password = password + consonant
            vowel = vowels[random.randint(1, len(vowels) - 1)]
            if random.choice([1,0]):
                vowel = vowel.upper()
            password = password + vowel

        return password

    def pagination_widget(self, total, start, href, ptype='forum'):
        """ A Pagination Widget """

        # total = total number of results
        # start = zero-based index of first result to be displayed (e.g.
        # page 3 of 5 10-batch pages starts with 20)
        # href  = url + necessary querystring for your results

        # Items per page
        if ptype == 'forum':
            batch = int(self.get_system_property('zfsp_threads_per_page', 15))
        elif ptype == 'topic':
            batch = int(self.get_system_property(
                'zfsp_responses_per_page', 15))
        elif ptype == 'admin_users':
            batch = 50
        else:
            batch = 15

        # current page number. add first to prevent zero division errors.
        current = (start + batch) / batch

        # total number of pages. use ceiling to catch a remainder.
        pages = int(math.ceil(float(total) / float(batch)))

        # Need to modify the widget to return a more user-friendly pagination
        # UI, in the form:
        # [Previous 10] [Previous] 1 2 3 4 5 6 7 [8] 9 10 [Next] [Next 10]
        # If Click on "next 10" then show:
        # [Previous 10] [Previous] 11 12 13 14 15 16 17 [18] 19 20 [Next]
        #     [Next 10]
        # Assuming there are 25 "pages":
        # [Previous 10] [Previous] 21 22 23 24 [25] [Next] [Next 10]
        # Things to consider:
        # - If on page 28 of a 32 page widget, click on "Next 10" must go to
        # the "last" (32) number, not 38
        # - "Previous", "Previous 10", "Next" and "Next 10" must be disabled
        # when appropriate

        PAGE_SET = 10
        sets_to_display = pages / PAGE_SET
        reminder_pages  = pages % PAGE_SET
        if reminder_pages:
            extra_page = 1
        else:
            extra_page = 0
        sets_to_display += extra_page

        real_sets_to_display = total / float(batch)

        if real_sets_to_display > 1:
            html_code = '<div class="breadcrumbs" style="text-align:center;"> '
            '<span i18n:translate="">Pages</span>:\n'

            if start >= (batch * PAGE_SET):
                html_code += '[<a class="breadcrumbs" href="'
                html_code += '%s?start=%s">Previous %s</a>]&nbsp;' % (
                    href, start - (batch * PAGE_SET), PAGE_SET)

            if start - batch >= 0:
                html_code += '[<a class="breadcrumbs" href='
                html_code += '"%s?start=%s" title="">Previous</a>]&nbsp;' % (
                    href, start - batch)

            # Need to find the right "range", for example on a 10-page set of
            # 3-results-per-page for 44 total results,
            # If I click page 6, the range must be 1 2 3 4 5 6 7 8 9 10
            # If I am on page 11, then click on 15, the range must be 11 12
            # 13 14 15 16 17 18 19 20
            # and so on (Note 16 17 18 19 20 must be disabled)
            start_number = 0
            end_number = PAGE_SET
            mid_number = (start / batch) + 1
            while 1:
                if mid_number >= start_number and mid_number <= end_number:
                    break
                start_number = end_number
                end_number = start_number + PAGE_SET

            page = start_number * batch

            this_range = range(1 + start_number, end_number + 1)

            for idx in this_range:
                if idx == (start + batch) / batch:
                    html_code += '<b>%s</b>&nbsp;' % str(idx)
                else:
                    if idx * batch - batch < total:
                        html_code += '<a class="breadcrumbs" href="'
                        html_code += '%s?start=%s" title="">%s</a>&nbsp;' % (
                            href, page, idx)

                page += batch

            if start + batch < total:
                html_code += '[<a class="breadcrumbs" href="'
                html_code += '%s?start=%s" title="">Next</a>]&nbsp;' % (
                    href, start + batch)

            if start + (batch * PAGE_SET) < total:
                tot = start + (batch * PAGE_SET)
                html_code += '[<a class="breadcrumbs" href="'
                html_code += '%s?start=%s" title="">Next %s</a>]&nbsp;' % (
                    href, tot, PAGE_SET)

            html_code += '</div>\n'
        else:
            html_code = ''

        return html_code
