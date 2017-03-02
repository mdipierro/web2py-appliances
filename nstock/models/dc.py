# -*- coding: utf-8 -*-
from app import Application
from gluon.storage import Storage
from gluon import current
from slugify import slugify
import uuid

if False:
    from gluon import Field, T, IS_NOT_EMPTY, IS_IN_SET, LOAD
    from db import db, auth, mail, myconf, plugins
    request = current.request


# configure global context
def _():
    current.auth = auth
    current.db = db
    current.mail = mail
    current.conf = myconf
    # set the language with dont need translation
    T.set_current_languages('en', 'en-en')
_()

# each content plugin must register here, for example for a text plugin:
# CT_REG.text = ContentPlugin()
#
# where ContentPlugin should be the text content-type implementation of
# ContentPlugin
CT_REG = Storage()

PUB_STATUS = (
    'canceled',  # canceled
    'usable',  # usable
    'withheld',  # withheld
)


def _get_slugline(f):
    f['slugline'] = slugify(f['headline'])

    return None


def _update_slugline(s, f):
    if 'headline' in f.keys():
        f['slugline'] = slugify(f['headline'])

    return None


db.define_table(
    'item',
    # content metadata
    Field('headline', 'string', length=512, default=''),
    Field('slugline', 'string', length=512, default=''),
    Field('keywords', 'list:string', default=''),
    Field('located', 'string', length=200, default=''),
    Field('genre', 'string', length=100, default=''),
    Field('section_page', 'string', length=100, default=''),
    # language of the item it self not the lenguage of the content
    Field(
        'language_tag',
        'string',
        default=T.accepted_language.split('-')[0],
        length=2),
    # item metadata
    Field('provider', 'string', length=100, default=''),
    Field('provider_service', 'string', default=''),
    Field('pubstatus', 'string', length=10, default='usable'),
    Field('embargoed', 'datetime', default=None),
    auth.signature,
    # copyright info.
    Field('copyright_holder', 'string', length=100, default=''),
    Field('copyright_url', 'string', length=512, default=''),
    Field('copyright_notice', 'text', default=''),
    # the item_type will be of use for searching the actions asociate with a
    # item in CONTENT_TYPE_REG, it should not be readed or writed by users
    # and should be writen only one, in the creation of the item.
    Field('item_type', 'string', length='100', default='text'),
    Field(
        'unique_id', 'string', length=64, default=uuid.uuid4(),
        writable=False, readable=False
    ),
)
db.item._before_insert.append(_get_slugline)
db.item._before_update.append(_update_slugline)
db.item.id.readable = False
db.item.id.writable = False
db.item.item_type.readable = False
db.item.item_type.writable = False
db.item.copyright_url.label = T('Copyright URL')
db.item.pubstatus.requires = IS_IN_SET(PUB_STATUS, zero=None)
db.item.pubstatus.label = T('Status')
db.item.headline.requires = IS_NOT_EMPTY()
db.item.headline.label = T('Headline')
db.item.headline.comment = T('Headline or descriptive title')
db.item.headline.requires = IS_NOT_EMPTY()
db.item.language_tag.label = T('Language')
db.item.keywords.label = T("Keywords")
db.item.keywords.requires = IS_NOT_EMPTY()
db.item.keywords.comment = T("One keyword per line")
db.item.section_page.label = T("Section")
db.item.section_page.comment = T(
    "Section or page in with this item is intended to be used")
db.item.located.label = T("Located")
db.item.located.comment = T(
    """
    It can be the name of a city or may contain details, for example: HAVANA,
    CUBA""")
db.item.genre.label = T('Genre')
db.item.genre.requires = IS_NOT_EMPTY()
db.item.provider.label = T("Provider")
db.item.provider.comment = T("""
It can be a descriptive name for the news provider or URL associated with it.
""")
db.item.provider_service.label = T("Provider service")
db.item.provider_service.comment = T("""
Allows the provider to declare which of its services, if any, delivered
this package.
""")
db.item.copyright_notice.label = T("Copyright Notice")
db.item.copyright_holder.label = T("Copyright Holder")
db.item.embargoed.label = T('Embargoed')
db.item.embargoed.comment = T(
    """
    News organisations often use an embargo to release information in advance,
    on the strict understanding that it may not be released into the public
    domain until after the embargo time has expired, or until some other form
    of permission has been given.
    """)

db.item._enable_record_versioning()

db.define_table(
    'languages',
    Field('language_tag', 'string', length=10),
    Field('english_name', 'string', length=30)
)


def _():
    """
    load language file into language table
    """
    import os
    import csv
    f_name = os.path.join(
        request.folder,
        os.path.join('private', 'language-codes.csv'))
    with open(f_name) as lang_codes:
        reader = csv.DictReader(lang_codes)
        for row in reader:
            db.languages.insert(
                language_tag=row['alpha2'],
                english_name=row['English']
            )
if db(db.languages.id > 0).count() == 0:
    _()


def _ltag_represent(v, r):
    value = db.languages(language_tag=v)
    if value is not None:
        return value.english_name

    return v
db.item.language_tag.represent = _ltag_represent


# notification center
def _():
    tbl = db.define_table(
        'notification',
        Field('subject', 'string', length=500),
        Field('message_content', 'text'),
        Field('from_user', 'reference auth_user'),
        Field('to_user', 'reference auth_user'),
        Field('seen', 'boolean', default=False),
        Field('msg_date', 'datetime', default=request.now)
    )
    tbl.subject.label = T('Subject')
    tbl.message_content.label = T('Message')
    tbl.from_user.label = T('From')
    tbl.msg_date.label = T('Date and Time')
    tbl.seen.label = T('Seen')
    tbl.to_user.readable = False
    tbl.id.readable = False
_()


# orgs are going here
def _():
    # don't polute globals()
    tbl = db.define_table(
        'desk',
        Field('name', 'string', length=100),
        Field('item_list', 'list:reference item', default=[])
    )
    tbl.name.label = T('Name')
    tbl.item_list.readable = False

    tbl = db.define_table(
        'organization',
        Field('name', 'string', length=100),
        Field('description', 'text'),
        Field('users', 'list:reference auth_user', default=[]),
        Field('desks', 'list:reference desk', default=[])
    )
    tbl.name.label = T('Name')
    tbl.description.label = T('Description')
    tbl.users.label = T('Users')
_()

# register content type plugins
application = Application()
plugins.text.app = application
plugins.picture.app = application
plugins.photoset.app = application
plugins.package.app = application
