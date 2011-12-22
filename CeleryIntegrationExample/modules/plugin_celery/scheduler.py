import os
import logging
from datetime import datetime, timedelta
from multiprocessing.util import Finalize
from time import time
from anyjson import deserialize, serialize
from celery import schedules
from celery.beat import Scheduler, ScheduleEntry
from celery.utils.timeutils import timedelta_seconds
from celeryconfig import CELERY_RESULT_DBURI

import sys, os
sys.path.append(os.environ['WEB2PY_PATH'])

from gluon import DAL
folder, uri = os.path.split(CELERY_RESULT_DBURI.split(':///')[1])
db=DAL(CELERY_RESULT_DBURI.split(':///')[0]+'://'+uri,folder=folder,
       migrate_enabled=False,auto_import=True)
print 'I found these table: ' +', '.join(db.tables())
if db(db.celery_periodictasks).count()>0:
    logging.error('found too many db.celery_periodictasks, deleting them all')
    db(db.celery_periodictasks).delete()
if db(db.celery_periodictasks).count()<1:
    logging.error('found no db.celery_periodictasks, making a singleton')
    db.celery_periodictasks(last_update=datetime.now())

def get_or_make_unique(table,**fields):
    query = reduce(lambda a,b:a&b,[table[key]==value for key,value in fields.items()])
    rows = table._db(query).select(limitby=(0,2))
    if len(rows)>1:
        table._db(query).delete()
        rows=[]
    if len(rows)==1:
        row = rows[0].id
    else:
        row = table.insert(**fields)
    db(db.celery_periodictasks).update(last_update=datetime.now())
    db.commit()
    return row

class ModelEntry(ScheduleEntry):
    save_fields = ["last_run_at", "total_run_count", "no_changes"]

    def __init__(self, record):
        self.name = record.name
        self.task = record.task
        if record.interval:
            i = record.interval
            self.schedule = schedules.schedule(timedelta(**{i.period: i.every}))
        else:
            i = record.crontab
            schedules.crontab(minute=i.minute,
                              hour=i.hour,
                              day_of_week=i.day_of_week)
        try:
            self.args = deserialize(record.args or u"[]")
            self.kwargs = deserialize(record.kwargs or u"{}")
        except ValueError:
            record.update_record(no_changes = True, enabled = False)
            db(db.celery_periodictasks).update(last_update=datetime.now())
            db.commit()
            raise

        self.options = {"queue": record.queue,
                        "exchange": record.exchange,
                        "routing_key": record.routing_key,
                        "expires": record.expires}
        self.total_run_count = record.total_run_count or 0
        self.record = record        
        if not record.last_run_at:
            record.update_record(last_run_at = datetime.now())
            db(db.celery_periodictasks).update(last_update=datetime.now())
            db.commit()
        self.last_run_at = record.last_run_at
            
    def is_due(self):
        if not self.record.enabled:
            return False, 5.0   # 5 second delay for re-enable.
        return self.schedule.is_due(self.last_run_at)

    def next(self):
        self.record.update_record(
            last_run_at = datetime.now(),
            total_run_count = (self.record.total_run_count or 0) + 1,
            no_changes = True)
        db(db.celery_periodictasks).update(last_update=datetime.now())
        db.commit()
        return ModelEntry(self.record)

    def save(self):
        # nothing needs to be done
        pass

    @staticmethod
    def to_model_schedule(schedule):
        if schedule.__class__ == schedules.schedule:
            row = get_or_make_unique(db.celery_intervalschedule,
                                     every=timedelta_seconds(schedule.run_every),
                                     period='seconds')
            return row, 'interval'
        elif schedule.__class__ == schedules.crontab:
            row = get_or_make_unique(db.celery_crontabschedule,
                                     minute=schedule._orig_minute,
                                     hour=schedule._orig_hour,
                                     day_of_week=schedule._orig_day_of_week)
            return row, 'crontab'
        else:
            raise ValueError("Can't convert schedule type %r to model" % schedule)

    @staticmethod
    def from_entry(name, skip_fields=("relative", "options"), **entry):
        fields = dict(entry)
        for skip_field in skip_fields:
            fields.pop(skip_field, None)
        schedule = fields.pop("schedule")
        model_schedule, model_field = ModelEntry.to_model_schedule(schedule)
        fields[model_field] = model_schedule
        fields["args"] = serialize(fields.get("args") or [])
        fields["kwargs"] = serialize(fields.get("kwargs") or {})
        row = db.celery_periodictask(name=name)
        if row:
            row.update_record(**fields)
        else:
            row = db.celery_periodictask.insert(**fields)
        db(db.celery_periodictasks).update(last_update=datetime.now())
        db.commit()
        return ModelEntry(row)

    def __repr__(self):
        return "<ModelEntry: %s %s(*%s, **%s) {%s}" % (self.name,
                                                        self.task,
                                                        self.args,
                                                        self.kwargs,
                                                        self.schedule)



class Web2pyScheduler(Scheduler):
    _schedule = None
    _last_timestamp = None

    def __init__(self, *args, **kwargs):
        self._dirty = set()
        self._last_flush = None
        self._flush_every = 3 * 60
        self._finalize = Finalize(self, self.flush, exitpriority=5)
        Scheduler.__init__(self, *args, **kwargs)
        self.max_interval = 5

    def setup_schedule(self):
        self.install_default_entries(self.schedule)
        self.update_from_dict(self.app.conf.CELERYBEAT_SCHEDULE)

    def all_as_schedule(self):
        self.logger.debug("DatabaseScheduler: Fetching database schedule")
        s = {}
        for record in db(db.celery_periodictask.enabled==True).select():
            print record
            try:
                s[record.name] = ModelEntry(record)
            except ValueError:
                pass
        return s

    def schedule_changed(self):
        if self._last_timestamp is not None:
            # If MySQL is running with transaction isolation level
            # REPEATABLE-READ (default), then we won't see changes done by
            # other transactions until the current transaction is
            # committed (Issue #41).
            # db.commit()
            row = db(db.celery_periodictasks).select().first()
            if not row or row.last_update < self._last_timestamp:
                return False
        self._last_timestamp = datetime.now()
        return True

    def should_flush(self):
        return not self._last_flush or \
                    (time() - self._last_flush) > self._flush_every

    def reserve(self, entry):
        new_entry = Scheduler.reserve(self, entry)
        # Need to story entry by name, because the entry may change
        # in the mean time.
        self._dirty.add(new_entry.name)
        if self.should_flush():
            self.logger.debug("Celerybeat: Writing schedule changes...")
            self.flush()
        return new_entry

    def flush(self):
        if not self._dirty:
            return
        self.logger.debug("Writing dirty entries...")
        try:
            while self._dirty:
                name = self._dirty.pop()
                if name in self.schedule: self.schedule[name].save() 
        except:
            db.rollback()
            raise
        else:
            db(db.celery_periodictasks).update(last_update=datetime.now())
            db.commit()
            self._last_flush = time()

    def update_from_dict(self, dict_):
        s = {}
        for name, entry in dict_.items():
            try:
                s[name] = ModelEntry.from_entry(name, **entry)                
            except Exception, exc:
                self.logger.error(
                    "Couldn't add entry %r to database schedule: %r. "
                    "Contents: %r" % (name, exc, entry))
        self.schedule.update(s)

    def get_schedule(self):
        if self.schedule_changed():
            self.flush()
            self.logger.debug("DatabaseScheduler: Schedule changed.")
            self._schedule = self.all_as_schedule()
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(
                    "Current schedule:\n" +
                    "\n".join(repr(entry)
                              for entry in self._schedule.values()))
            self.flush()
        return self._schedule

