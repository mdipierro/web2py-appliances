# -*- coding: utf-8 -*-
from gluon import current


def item_notify_users(item_id, subject='None', message='None'):
    """
    Notify all users who has access to item_id
    """
    db = current.db
    mail = current.mail
    auth = current.auth

    item = db.item(item_id)

    # i need all user who have some permission over current item
    query = (db.auth_permission.record_id == item.id)
    query &= (db.auth_permission.table_name == db.item)
    query &= (db.auth_permission.group_id == db.auth_membership.group_id)
    query &= (db.auth_user.id == db.auth_membership.user_id)
    # except the user who active this action
    query &= (db.auth_user.id != auth.user.id)

    for u in db(query).select(db.auth_user.ALL, distinct=True):
        mail.send(
            to=[u.email],
            subject=subject,
            message=message
        )
