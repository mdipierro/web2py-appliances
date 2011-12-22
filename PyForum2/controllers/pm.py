@auth_user.requires_login()
def index():
    view_info = {}
    view_info.update({'errors': []})
    user_id = auth_user.get_user_id()
    req = request.vars
    form_submitted = req.form_submitted

    if req.new_b:
        redirect(URL(r=request, c='pm', f='message_new'))
    else:
        if req.empty_b:
            # Get our "trash" category
            trash_cat_id = db(db.zf_pm_categories.name.lower() == \
                              'trash').select()[0].id
            # Remove the messages in the trash
            db((db.zf_pm.user_id == user_id) &
                (db.zf_pm.cat_id==trash_cat_id)).delete()

        if req.move_b:
            # 1. Get the target category selected in the dropdown
            target_cat_id = req.moveto
            #raise ValueError, req
            if len(target_cat_id):
                move_ids = []
                # Get the ids that need to be moved:
                for req_var in req:
                    if req_var[:13] == 'remove_pm_id_':
                        move_ids.append(req[req_var])
                # Ok, now perform the move if there is anything to move
                if move_ids:
                    for pm_id in move_ids:
                        db((db.zf_pm.user_id == user_id) &
                            (db.zf_pm.id == int(pm_id))).update(
                            cat_id=int(target_cat_id))

        # continuing..
        # Get categories:
        cats = db().select(db.zf_pm_categories.ALL,
                           orderby=db.zf_pm_categories.display_order)
        if len(request.args):
            default_cat = [def_cat for def_cat in cats \
                           if def_cat.id == int(request.args[0])][0]
        else:
            default_cat = cats[0]
        view_info.update({'default_cat': default_cat})


        # Here get the number of unread messages per category
        unread_dict = {}
        read_unread_dict = {}
        for cat in cats:

            unread_msgs = db((db.zf_pm.cat_id == cat.id) &
                (db.zf_pm.read_flag == False) &
                (db.zf_pm.user_id == user_id)).count()
            unread_dict.update({cat.id: unread_msgs})

            read_unread_msgs = db((db.zf_pm.cat_id == cat.id) &
                (db.zf_pm.user_id == user_id)).count()
            read_unread_dict.update({cat.id: read_unread_msgs})

        view_info.update({'unread_dict': unread_dict})
        view_info.update({'read_unread_dict': read_unread_dict})

        # Get Messages for selected category
        messages = db((db.zf_pm.cat_id == default_cat.id) &
            (db.zf_pm.user_id == user_id)).select(
            db.zf_pm.ALL, orderby=~db.zf_pm.creation_date)
        return dict(request=request, view_info=view_info,
                    cats=cats, messages=messages)

@auth_user.requires_login()
def message_new():
    view_info = {}
    view_info.update({'errors': []})
    user_id = auth_user.get_user_id()
    req = request.vars
    # v1.1+ mto is now the ID (auth_users.id) if the recipient,
    # NOT a string or username anymore
    if len(request.args) > 0:
        mto = request.args[0]
    else:
        mto = ''
    if req.new_b:
        subject = parse_content(req.subject.strip())
        new_msg = parse_content(req.new_msg.strip())
        if not mto:
            view_info['errors'].append('Recipient must be specified')
        if not subject:
            view_info['errors'].append('Subject must be specified')
        if not new_msg:
            view_info['errors'].append('Message content is required')

        if not view_info['errors']:
            # See if target user exists
            dest_user_info = db((db.auth_users.id == mto) &
                (db.auth_users.is_enabled == True)).select()
            if not len(dest_user_info):
                view_info['errors'].append('The recipient does not appear '
                                           'to exist, is invalid or is a user '
                                           'that has been banned from the '
                                           'system')
        if view_info['errors']:
            return dict(request=request, view_info=view_info, mto=mto)
        else:
            # "Send" the message
            inbox_cat_id = db(db.zf_pm_categories.name.lower() ==
                              'inbox').select()[0].id
            db.zf_pm.insert(
                cat_id=inbox_cat_id,
                read_flag=False,
                user_id=mto,
                from_user_id=user_id,
                subject=subject,
                message=new_msg,
                creation_date=request.now)
            # "Send" a message to myself
            sent_cat_id = db(db.zf_pm_categories.name.lower() ==
                             'sent').select()[0].id
            db.zf_pm.insert(cat_id=sent_cat_id, read_flag=True,
                            user_id=user_id,
                            from_user_id=user_id,
                            subject=subject,
                            message=new_msg,
                            creation_date=request.now)
            redirect(URL(r=request, c='pm', f='index'))
    else:
        # Check if this user exists first
        if mto and not db(db.auth_users.id == mto).count():
            redirect(URL(r=request, c='default', f='invalid_request'))
        return dict(request=request, view_info=view_info, mto=mto)

@auth_user.requires_login()
def view():
    view_info = {}
    view_info.update({'errors': []})
    user_id = auth_user.get_user_id()
    req = request.vars
    if req.form_submitted:
        msg_id = int(req.msg_id)
        msg = db((db.zf_pm.id == msg_id) &
            (db.zf_pm.user_id == user_id)).select()[0]
        # Basically means that there was a response for this message
        if req.reply_b:
            # 1. Send the reply
            response_msg = req.response_msg.strip()
            if response_msg:
                # Grab our "inbox"
                inbox_cat_id = db(db.zf_pm_categories.name.lower() ==
                                  'inbox').select()[0].id
                re_subject = 'RE. %s' % (msg.subject)
                re_message = "%s\n\n%s\nOriginal Message\n\n%s" % (
                    parse_content(response_msg), ('=' * 30), msg.message)
                # "Send" the message to the destination user
                db.zf_pm.insert(cat_id=inbox_cat_id, read_flag=False,
                                user_id=msg.from_user_id,
                                from_user_id=user_id,
                                subject=re_subject,
                                message=re_message, creation_date=request.now)
                # "Send" a message to myself
                sent_cat_id = db(db.zf_pm_categories.name.lower() ==
                                 'sent').select()[0].id
                db.zf_pm.insert(cat_id=sent_cat_id, read_flag=True,
                                user_id=user_id,
                                from_user_id=user_id,
                                subject=re_subject,
                                message=re_message,
                                creation_date=request.now)
            # 3. return back to the PM index page
            redirect(URL(r=request, c='pm', f='index'))
    else:
        if len(request.args):
            msg_id = int(request.args[0])
            m = db((db.zf_pm.id == msg_id) &
                (db.zf_pm.user_id == user_id)).select()
            if len(m):
                msg = m[0]
                # flag it as read
                db(db.zf_pm.id==msg.id).update(read_flag=True)
                # Send it to the view
                return dict(request=request, view_info=view_info, msg=msg)
            else:
                redirect(URL(r=request, c='default', f='invalid_request'))
        else:
            redirect(URL(r=request, c='default', f='invalid_request'))
