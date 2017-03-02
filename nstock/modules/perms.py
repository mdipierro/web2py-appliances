# coding=utf-8
from gluon import current


def isOwnerOrCollaborator(item_id=None):
    """
    Returns True if the current user is the owner or has collaborator
    permission
    """
    request = current.request

    if not item_id:
        item_id = request.args(0)

    return (isOwner(item_id) or isCollaborator(item_id))


def isOwner(item_id):
    """
    Returns True only if the current user is the owner of the item
    """
    auth = current.auth
    db = current.db

    return auth.has_permission('owner', db.item, record_id=item_id)


def isCollaborator(item_id):
    """
    Returns True if the current user has collaborator permission over item_id
    """
    auth = current.auth
    db = current.db

    return auth.has_permission('collaborator', db.item, record_id=item_id)
