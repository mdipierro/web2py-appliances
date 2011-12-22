def _():

    from gluon.storage import Storage
    try:
        from celery import states
    except ImportError:
        raise HTTP(200,"requires celery, celery not installed")

    db = DAL('sqlite://plugin_celery.db')
    
    HEARTBEAT_EXPIRE = 150      # 2 minutes, 30 seconds
    TASK_STATE_CHOICES = zip(states.ALL_STATES, states.ALL_STATES)
    PERIOD_CHOICES = (("days", T("Days")),
                      ("hours", T("Hours")),
                      ("minutes", T("Minutes")),
                      ("seconds", T("Seconds")),
                      ("microseconds", T("Microseconds")))
    TASK_STATE_COLORS = {states.SUCCESS: "green",
                         states.FAILURE: "red",
                         states.REVOKED: "magenta",
                         states.STARTED: "yellow",
                         states.RETRY: "orange",
                         "RECEIVED": "blue"}
    NODE_STATE_COLORS = {"ONLINE": "green",
                         "OFFLINE": "gray"}

    WORKER_UPDATE_FREQ = 60  # limit worker timestamp write freq.

    taskmeta = db.define_table(
        'celery_taskmeta',
        Field('task_id',length=255,unique=True),
        Field('status',length=50,default=states.PENDING,
              requires=IS_IN_SET(TASK_STATE_CHOICES)),
        Field('result','text',default=''),
        Field('date_done','datetime',default=request.now),
        Field('traceback','text',default=None))

    tasksetmeta = db.define_table(
        'celery_tasksetmeta',
        Field('taskset_id',length=255,unique=True),
        Field('result','text',default=''),
        Field('date_done','datetime',default=request.now))

    intervalschedule = db.define_table(
        'celery_intervalschedule',
        Field('every','integer',notnull=True),
        Field('period',length=24,
              requires=IS_IN_SET(PERIOD_CHOICES)),
        format='every %(every)s %(period)s')        

    crontab = db.define_table(
        'celery_crontabschedule',
        Field('minute',length=64,default='*'),
        Field('hour',length=64,default='*'),
        Field('day_of_week',length=64,default='*'),
        format='%(minute)s %(hour)s %(day_of_week)s')        

    periodictasks = db.define_table(  ### this table muct contain a single record
        'celery_periodictasks',
        Field('last_update','datetime',notnull=True))

    periodictask = db.define_table(
        'celery_periodictask',
        Field('name',length=200,unique=True),
        Field('task',length=200),
        Field('interval',intervalschedule,
              requires=IS_NULL_OR(IS_IN_DB(db,intervalschedule.id,
                                           intervalschedule._format))),
        Field('crontab',crontab,
              requires=IS_NULL_OR(IS_IN_DB(db,crontab.id,
                                           crontab._format))),
        Field('args','text',default='[]'),
        Field('kwargs','text',default='{}'),
        Field('queue',length=200),
        Field('exchange',length=200),
        Field('routing_key',length=200),
        Field('expires','datetime',default=None),
        Field('enabled','boolean',default=True),
        Field('last_run_at','datetime',writable=False,default=None),
        Field('total_run_count','integer',default=0),
        Field('date_changed','datetime',
              default=request.now,update=request.now))

    workerstate = db.define_table(
        'celery_workerstate',
        Field('hostname',length=255,unique=True),
        Field('last_heartbeat','datetime')) # requires an index!

    taskstate = db.define_table(
        'celery_taskstate',
        Field('state',length=64,
              requires=IS_IN_SET(TASK_STATE_CHOICES)), # requires index
        Field('task_id',unique=True), # a UUID
        Field('name',length=200), # requires index
        Field('tstamp','datetime'), # requires index
        Field('args','text'),
        Field('kwargs','text'),
        Field('eta','datetime',label='Date to Execute'),
        Field('expires','datetime'),
        Field('result','text'),
        Field('traceback','text'),
        Field('runtime','double'), # in seconds
        Field('retries','integer',default=0),
        Field('worker','string'),
        Field('hidden','boolean',default=False,
              writable=False,readable=False))

    return Storage(locals())
plugin_celery = _()
plugin_celery_db = plugin_celery.db
