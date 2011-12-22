from datetime import datetime
from celery.utils.timeutils import maybe_iso8601
from celery.events.snapshot import Polaroid
from celeryconfig import CELERY_RESULT_DBURI
import sys, os
sys.path.append(os.environ['WEB2PY_PATH'])

from gluon import DAL
folder, uri = os.path.split(CELERY_RESULT_DBURI.split(':///')[1])
print uri, folder
db=DAL(CELERY_RESULT_DBURI.split(':///')[0]+'://'+uri,folder=folder,
       migrate_enabled=False,auto_import=True)

print 'I found these table: ' +', '.join(db.tables())

worker_mapping = {}

class Web2pyCamera(Polaroid):    
    def shutter(self,state=None):
        if not state: state = self.state # for backward compatibility
        if not state or not state.event_count:
            # No new events since last snapshot.            
            print '...'
            return        
        print("Total: %s events, %s tasks" % (
            state.event_count, state.task_count))
        self.sync_workers(state.workers)
        self.sync_tasks(state.tasks)
    def sync_workers(self,workers):
        for hostname,worker in workers.items():
            last_heartbeat=datetime.fromtimestamp(worker.heartbeats[-1])
            d = dict(last_heartbeat=last_heartbeat)
            if hostname in worker_mapping:
                db(db.celery_workerstate.id==worker_mapping[hostname]).update(**d)
            else:
                row = db.celery_workerstate(hostname=hostname)
                if row:                    
                    row.update_record(**d)
                    id = row.id
                else:
                    id = db.celery_workerstate.insert(hostname=hostname,**d)
                worker_mapping[hostname] = id
        db.commit()
    def sync_tasks(self,tasks):        
        for task_id,task in tasks.items():
            row = db.celery_taskstate(task_id=task_id)
            d = {"name": task.name,
                 "args": task.args,
                 "kwargs": task.kwargs,
                 "eta": maybe_iso8601(task.eta),
                 "expires": maybe_iso8601(task.expires),
                 "state": task.state,
                 "tstamp": datetime.fromtimestamp(task.timestamp),
                 "result": task.result or task.exception,
                 "traceback": task.traceback,
                 "runtime": task.runtime,
                 "worker": task.worker.hostname}
            row = db.celery_taskstate(task_id=task_id)
            if row: row.update_record(**d)
            else: db.celery_taskstate.insert(task_id=task_id,**d)
        db.commit()
