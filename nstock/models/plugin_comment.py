# -*- coding: utf-8 -*-
if False:
    from gluon import Field, LOAD, IS_NOT_EMPTY
    from gluon import current
    T = current.T
    from db import db, auth
"""
Define the tables for the editorials commentary system
"""


def _():
    tbl = db.define_table(
        'plugin_comment_comment',
        Field('body', 'text', label=T('Your comment')),
        Field('item_id', 'string', length=64),
        auth.signature,
    )
    tbl.item_id.readable = False
    tbl.item_id.writable = False
    tbl.body.requires = IS_NOT_EMPTY()

    return lambda item_id: LOAD(
        'plugin_comment', 'index.load', args=[item_id], ajax=True)

plugin_comment = _()


def _():
    return lambda item_id: LOAD(
        'plugin_comment',
        'index.load',
        args=[item_id],
        vars=dict(short=True),
        ajax=True)
plugin_comment_short = _()
