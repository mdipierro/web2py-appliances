# -*- coding: utf-8 -*-
if False:
    from gluon import current
    response = current.response
    request = current.request
    T = current.T
    from dc import application
    from db import auth


def _():
    # add items menu
    create_items = []
    registry = application.registry
    for content_type in registry:
        url, title = registry[content_type].create_item_url()
        create_items.append(
            (title, False, url, [])
        )
    response.menu += [(T('Add Items'), False, "#", create_items)]

if auth.user:
    _()
