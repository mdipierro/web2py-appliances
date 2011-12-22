from datetime import timedelta
from celery.task import Task, PeriodicTask
import time

__all__ = ['DemoTaskFast','DemoTaskSlow','DemoTaskError','DemoTaskPeriodic']

class DemoTaskFast(Task):
    def run(self, *args, **vars):
        t = 1
        print 'DemoTaskFast sleeping %i seconds' % t
        time.sleep(t)
        return vars.get('response',True)

class DemoTaskSlow(Task):
    def run(self, *args, **vars):
        t = 30
        print 'DemoTaskSlow sleeping %i seconds' % t
        time.sleep(t)
        return vars.get('response',True)

class DemoTaskError(Task):
    def run(self, *args, **vars):
        print 'DemoTaskError'
        1/0
        return True

class DemoTaskPeriodic(PeriodicTask):
    run_every = timedelta(seconds=60)
    def run(self, **kwargs):
        print 'DemoTaskPeriodic'
        return True
