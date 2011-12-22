# coding: utf8
# try something like
is_phone = IS_MATCH('^(\+\d{2}\-)?[\d\-]*(\#\d+)?$')
import datetime, time
systemd=DAL("sqlite://serverStatistics.db")

"""
Table definition
"""

systemd.define_table("provider",
      Field("name", notnull=True, default=None),
      Field('url'),
      Field('email'),
      Field('address'),
      Field('movile_phone'),
      Field('land_line'),
      Field('fax'))

systemd.define_table("platform",
      SQLField("name", notnull=True, default=None),
      SQLField("id_provider", systemd.provider),
      SQLField("created_on", "datetime", notnull=True, default=request.now))

systemd.platform.id_provider.requires=IS_IN_DB(systemd,'provider.id','provider.name')


systemd.provider.name.requires=[IS_NOT_EMPTY(),IS_NOT_IN_DB(systemd,'provider.name')]
systemd.provider.url.requires=IS_EMPTY_OR(IS_URL())
systemd.provider.movile_phone.requires=is_phone
systemd.provider.land_line.requires=is_phone
systemd.provider.fax.requires=is_phone


"""
Table definition
"""
systemd.define_table("server_type",
      SQLField("name", default=None))


"""
Table definition
"""
systemd.define_table("server",
      SQLField("id_platform", systemd.platform),
      SQLField("name", notnull=True, default=None),
      SQLField("ip", notnull=True, default=None),
      SQLField("port", "integer", notnull=True, default=22),
      SQLField("id_server_type", systemd.server_type),
      SQLField("created_on", "datetime", notnull=True, default=request.now))


"""
Relations between tables (remove fields you don't need from requires)
"""
systemd.server.id_platform.requires=IS_IN_DB(systemd, 'platform.id','platform.name','platform.created_on')
systemd.server.id_server_type.requires=IS_IN_DB(systemd, 'server_type.id','server_type.name')
