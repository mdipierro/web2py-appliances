# coding: utf-8
if False:
    from gluon import current, SQLFORM, I, XML
    response = current.response
    request = current.request
    from db import db, auth


@auth.requires_login()
def index():
    """
    Show notifications for the current user
    """
    tbl = db.notification
    query = (tbl.id > 0)
    query &= (tbl.to_user == auth.user.id)

    def p_seen_rpr(v, r):
        if v:
            return I(_class="fa fa-envelope-open-o")

        return I(_class="fa fa-envelope")
    tbl.seen.represent = p_seen_rpr

    if request.args(0) == 'view':
        tbl.seen.readable = False
        tbl.message_content.represent = lambda v, r: XML(v)
        msg = tbl(request.args(2))
        msg.update_record(seen=True)
        tbl.from_user.represent = lambda v, r: db.auth_user(v).email

    grid = SQLFORM.grid(
        query,
        fields=[tbl.subject, tbl.from_user, tbl.seen, tbl.msg_date],
        paginate=10,
        showbuttontext=False,
        editable=False,
        csv=False,
        maxtextlengths={'notification.subject': 100},
        create=False,
        searchable=False,
        orderby=[~tbl.msg_date],
        formstyle='bootstrap',
    )

    return dict(grid=grid)


@auth.requires_login()
def has_notifications():
    query = (db.notification.id > 0)
    query &= (db.notification.seen == False)
    query &= (db.notification.to_user == auth.user.id)

    nots = db(query).select(db.notification.ALL)

    if nots:
        return response.json(True)

    return response.json(False)
